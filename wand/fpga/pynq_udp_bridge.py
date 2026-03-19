"""
Notebook-friendly Wand-Brain UDP bridge for PYNQ.

Purpose:
- keep the existing camera / FPGA centroid pipeline unchanged
- add a minimal control-plane preflight check
- package valid centroid points into wb-point-v1 UDP packets
- group visible-point runs into strokes
- send an explicit STROKE_END packet after a short no-blob gap

This module is intentionally standard-library only so it can be imported
from a Jupyter notebook on PYNQ without extra dependency work.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import socket
import struct
import time
import urllib.request


WB_STRUCT = struct.Struct("<HBBHHIIhhI")
WB_MAGIC = 0x5742
WB_VERSION = 1
Q15_MAX = 32767

PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04


def monotonic_ms_u32() -> int:
    return (time.monotonic_ns() // 1_000_000) & 0xFFFFFFFF


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def to_q15(value: float) -> int:
    return int(round(clamp01(value) * Q15_MAX))


@dataclass
class WandBrainConfig:
    brain_host: str
    brain_udp_port: int = 41000
    brain_api_port: int = 8000
    device_number: int = 1
    wand_id: int = 1
    starting_stroke_id: int = 1
    starting_packet_number: int = 0
    gap_timeout_ms: int = 220
    mirror_x: bool = False
    mirror_y: bool = False
    preflight_timeout_s: float = 3.0
    control_timeout_s: float = 2.0


class WandBrainUdpBridge:
    """
    Stateful sender for notebook loops.

    Stroke policy:
    - first valid point after an idle period starts a new stroke
    - every valid point sends one UDP packet
    - after `gap_timeout_ms` with no valid points, one final STROKE_END
      packet is sent using the last valid point
    """

    def __init__(self, config: WandBrainConfig):
        self.cfg = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.packet_number = config.starting_packet_number
        self.next_stroke_id = max(1, config.starting_stroke_id)

        self.active_stroke_id: int | None = None
        self.last_valid_ms: int | None = None
        self.last_valid_q15: tuple[int, int] | None = None
        self.last_sent_frame_id: int | None = None
        self.sent_points_in_stroke = 0

    def close(self) -> None:
        self.sock.close()

    @property
    def has_active_stroke(self) -> bool:
        return self.active_stroke_id is not None

    def _http_json(
        self,
        *,
        method: str,
        path: str,
        payload: dict | None = None,
        timeout_s: float | None = None,
    ) -> dict:
        url = f"http://{self.cfg.brain_host}:{self.cfg.brain_api_port}{path}"
        data = None
        headers: dict[str, str] = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout_s or self.cfg.control_timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def preflight_check(self) -> dict:
        payload = self._http_json(
            method="GET",
            path="/api/v1/health",
            timeout_s=self.cfg.preflight_timeout_s,
        )
        if not payload.get("ok"):
            raise RuntimeError(f"Wand-Brain health check failed: {payload}")
        return payload

    def get_node_control(self) -> dict:
        return self._http_json(
            method="GET",
            path=f"/api/v3/node/{self.cfg.device_number}/control",
        )

    def ack_node_control(self, payload: dict) -> dict:
        return self._http_json(
            method="POST",
            path=f"/api/v3/node/{self.cfg.device_number}/ack",
            payload=payload,
        )

    def _new_stroke_id(self) -> int:
        stroke_id = self.next_stroke_id
        self.next_stroke_id += 1
        return stroke_id

    def _normalize_xy(
        self,
        x_px: int,
        y_px: int,
        src_w: int,
        src_h: int,
    ) -> tuple[float, float]:
        if src_w <= 1 or src_h <= 1:
            raise ValueError("src_w and src_h must be > 1")

        x = x_px / float(src_w - 1)
        y = y_px / float(src_h - 1)

        if self.cfg.mirror_x:
            x = 1.0 - x
        if self.cfg.mirror_y:
            y = 1.0 - y

        return clamp01(x), clamp01(y)

    def _send_packet(
        self,
        *,
        stroke_id: int,
        x_q: int,
        y_q: int,
        timestamp_ms: int,
        flags: int,
    ) -> None:
        payload = WB_STRUCT.pack(
            WB_MAGIC,
            WB_VERSION,
            flags,
            self.cfg.device_number,
            self.cfg.wand_id,
            self.packet_number,
            stroke_id,
            x_q,
            y_q,
            timestamp_ms & 0xFFFFFFFF,
        )
        self.sock.sendto(payload, (self.cfg.brain_host, self.cfg.brain_udp_port))
        self.packet_number += 1

    def _end_stroke(self, timestamp_ms: int) -> bool:
        if self.active_stroke_id is None or self.last_valid_q15 is None or self.sent_points_in_stroke <= 0:
            self.active_stroke_id = None
            self.last_valid_ms = None
            self.last_valid_q15 = None
            self.last_sent_frame_id = None
            self.sent_points_in_stroke = 0
            return False

        x_q, y_q = self.last_valid_q15
        self._send_packet(
            stroke_id=self.active_stroke_id,
            x_q=x_q,
            y_q=y_q,
            timestamp_ms=timestamp_ms,
            flags=STROKE_END,
        )

        self.active_stroke_id = None
        self.last_valid_ms = None
        self.last_valid_q15 = None
        self.last_sent_frame_id = None
        self.sent_points_in_stroke = 0
        return True

    def process_point(
        self,
        *,
        valid: bool,
        x_px: int | None,
        y_px: int | None,
        src_w: int,
        src_h: int,
        timestamp_ms: int | None = None,
        frame_id: int | None = None,
    ) -> dict:
        """
        Call once per processed frame/result.

        Returns a small debug payload describing what happened:
        - action: "start", "point", "end", "idle", "skip_duplicate"
        - stroke_id
        - packet_number_after
        """
        now_ms = monotonic_ms_u32() if timestamp_ms is None else (timestamp_ms & 0xFFFFFFFF)

        if (
            valid
            and self.active_stroke_id is not None
            and frame_id is not None
            and self.last_sent_frame_id == frame_id
        ):
            # Re-reading the same valid FPGA result should keep the current
            # stroke alive even though we do not emit another UDP point.
            self.last_valid_ms = now_ms
            return {
                "action": "hold_duplicate",
                "stroke_id": self.active_stroke_id,
                "packet_number_after": self.packet_number,
            }

        if valid:
            if x_px is None or y_px is None:
                raise ValueError("x_px and y_px are required when valid=True")

            if self.active_stroke_id is None:
                self.active_stroke_id = self._new_stroke_id()
                action = "start"
                flags = STROKE_START | PEN_DOWN
            else:
                action = "point"
                flags = PEN_DOWN

            x_norm, y_norm = self._normalize_xy(x_px, y_px, src_w=src_w, src_h=src_h)
            x_q = to_q15(x_norm)
            y_q = to_q15(y_norm)

            self._send_packet(
                stroke_id=self.active_stroke_id,
                x_q=x_q,
                y_q=y_q,
                timestamp_ms=now_ms,
                flags=flags,
            )
            self.last_valid_ms = now_ms
            self.last_valid_q15 = (x_q, y_q)
            self.last_sent_frame_id = frame_id
            self.sent_points_in_stroke += 1

            return {
                "action": action,
                "stroke_id": self.active_stroke_id,
                "packet_number_after": self.packet_number,
                "x_norm": x_norm,
                "y_norm": y_norm,
            }

        if (
            self.active_stroke_id is not None
            and self.last_valid_ms is not None
            and (now_ms - self.last_valid_ms) >= self.cfg.gap_timeout_ms
        ):
            ended_stroke_id = self.active_stroke_id
            self._end_stroke(now_ms)
            return {
                "action": "end",
                "stroke_id": ended_stroke_id,
                "packet_number_after": self.packet_number,
            }

        return {
            "action": "idle",
            "stroke_id": self.active_stroke_id,
            "packet_number_after": self.packet_number,
        }

    def flush(self, timestamp_ms: int | None = None) -> bool:
        """
        Force-close the active stroke, typically in notebook cleanup.
        """
        now_ms = monotonic_ms_u32() if timestamp_ms is None else (timestamp_ms & 0xFFFFFFFF)
        return self._end_stroke(now_ms)
