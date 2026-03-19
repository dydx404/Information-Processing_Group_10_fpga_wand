#!/usr/bin/env python3
"""
Minimal Wand-Brain connectivity check.

Purpose:
- confirm the HTTP API is reachable
- send one small wb-point-v1 UDP stroke
- verify the exact attempt appears in Wand-Brain

This is intentionally notebook-friendly:
- import and call `run_connectivity_check(...)`
- or run as a CLI script
"""

from __future__ import annotations

import argparse
import json
import socket
import struct
import time
import urllib.error
import urllib.request

WB_STRUCT = struct.Struct("<HBBHHIIhhI")
MAGIC = 0x5742
VERSION = 1

PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04
Q15_MAX = 32767


def now_ms_u32() -> int:
    return int(time.time() * 1000) & 0xFFFFFFFF


def to_q15(v: float) -> int:
    return max(0, min(Q15_MAX, int(round(v * Q15_MAX))))


def get_json(url: str, timeout_s: float = 5.0) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_test_stroke(
    host: str,
    udp_port: int,
    *,
    device_number: int,
    wand_id: int,
    stroke_id: int,
    packet_start: int,
    points: int,
    interval_s: float,
    mode: str,
) -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_number = packet_start
    last_x_q = to_q15(0.5)
    last_y_q = to_q15(0.5)

    for i in range(points):
        t = i / max(1, points - 1)
        x = t
        y = t
        x_q = to_q15(x)
        y_q = to_q15(y)
        if mode == "visibility":
            flags = STROKE_START if i == 0 else 0
        else:
            flags = PEN_DOWN | (STROKE_START if i == 0 else 0)
        payload = WB_STRUCT.pack(
            MAGIC,
            VERSION,
            flags,
            device_number,
            wand_id,
            packet_number,
            stroke_id,
            x_q,
            y_q,
            now_ms_u32(),
        )
        sock.sendto(payload, (host, udp_port))
        packet_number += 1
        last_x_q = x_q
        last_y_q = y_q
        time.sleep(interval_s)

    if mode == "explicit":
        end_payload = WB_STRUCT.pack(
            MAGIC,
            VERSION,
            STROKE_END,
            device_number,
            wand_id,
            packet_number,
            stroke_id,
            last_x_q,
            last_y_q,
            now_ms_u32(),
        )
        sock.sendto(end_payload, (host, udp_port))
    sock.close()
    return packet_number + (1 if mode == "explicit" else 0)


def wait_for_attempt(
    host: str,
    api_port: int,
    *,
    wand_id: int,
    expected_source_stroke_id: int,
    min_start_ms: int,
    timeout_s: float,
) -> dict:
    deadline = time.time() + timeout_s
    url = f"http://{host}:{api_port}/api/v1/attempt/latest?wand_id={wand_id}"
    last_error = ""

    while time.time() < deadline:
        try:
            data = get_json(url, timeout_s=3.0)
            source_stroke_id = int(data.get("source_stroke_id", -1))
            start_ms = int(data.get("start_ms", -1))
            if source_stroke_id == expected_source_stroke_id and start_ms >= min_start_ms:
                return data
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(0.25)

    raise TimeoutError(
        f"timed out waiting for source_stroke_id={expected_source_stroke_id}; last_error={last_error}"
    )


def run_connectivity_check(
    host: str,
    *,
    api_port: int = 8000,
    udp_port: int = 41000,
    device_number: int = 1,
    wand_id: int = 1,
    stroke_id: int | None = None,
    packet_start: int = 0,
    points: int = 12,
    interval_s: float = 0.05,
    timeout_s: float = 8.0,
    mode: str = "explicit",
) -> dict:
    if stroke_id is None:
        stroke_id = int(time.time()) & 0x7FFFFFFF

    health_url = f"http://{host}:{api_port}/api/v1/health"
    health = get_json(health_url)
    if not health.get("ok"):
        raise RuntimeError(f"health check failed: {health}")
    idle_finalize_ms = int(health.get("idle_finalize_ms", 0))
    sent_after_ms = now_ms_u32()

    send_test_stroke(
        host,
        udp_port,
        device_number=device_number,
        wand_id=wand_id,
        stroke_id=stroke_id,
        packet_start=packet_start,
        points=points,
        interval_s=interval_s,
        mode=mode,
    )

    attempt = wait_for_attempt(
        host,
        api_port,
        wand_id=wand_id,
        expected_source_stroke_id=stroke_id,
        min_start_ms=sent_after_ms,
        timeout_s=max(timeout_s, (idle_finalize_ms / 1000.0) + 3.0) if mode == "visibility" else timeout_s,
    )

    if int(attempt["wand_id"]) != wand_id:
        raise RuntimeError(f"wand_id mismatch: {attempt}")
    if int(attempt["device_number"]) != device_number:
        raise RuntimeError(f"device_number mismatch: {attempt}")
    if int(attempt["num_points"]) <= 0:
        raise RuntimeError(f"num_points invalid: {attempt}")
    if mode == "visibility":
        close_reason = attempt.get("result", {}).get("close_reason")
        if close_reason != "idle_timeout":
            raise RuntimeError(f"expected idle_timeout close_reason in visibility mode, got: {attempt}")

    return {
        "ok": True,
        "health": health,
        "attempt": attempt,
        "summary": {
            "host": host,
            "udp_port": udp_port,
            "api_port": api_port,
            "device_number": device_number,
            "wand_id": wand_id,
            "source_stroke_id": stroke_id,
            "reported_attempt_id": int(attempt["attempt_id"]),
            "reported_points": int(attempt["num_points"]),
            "mode": mode,
            "close_reason": attempt.get("result", {}).get("close_reason"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Minimal Wand-Brain connectivity check.")
    ap.add_argument("--host", required=True, help="Wand-Brain host/IP")
    ap.add_argument("--api-port", type=int, default=8000)
    ap.add_argument("--udp-port", type=int, default=41000)
    ap.add_argument("--device", type=int, default=1)
    ap.add_argument("--wand", type=int, default=1)
    ap.add_argument("--stroke-id", type=int, default=None)
    ap.add_argument("--packet-start", type=int, default=0)
    ap.add_argument("--points", type=int, default=12, help="number of PEN_DOWN packets to send")
    ap.add_argument("--interval-ms", type=float, default=50.0, help="delay between packets")
    ap.add_argument("--timeout", type=float, default=8.0, help="seconds to wait for attempt")
    ap.add_argument(
        "--mode",
        choices=["explicit", "visibility"],
        default="visibility",
        help="`explicit` sends STROKE_END; `visibility` sends only visible-point packets and lets Brain idle-finalize",
    )
    args = ap.parse_args()

    result = run_connectivity_check(
        args.host,
        api_port=args.api_port,
        udp_port=args.udp_port,
        device_number=args.device,
        wand_id=args.wand,
        stroke_id=args.stroke_id,
        packet_start=args.packet_start,
        points=args.points,
        interval_s=args.interval_ms / 1000.0,
        timeout_s=args.timeout,
        mode=args.mode,
    )

    print("PASS: notebook/PYNQ connectivity confirmed")
    print(
        f"host={result['summary']['host']} "
        f"wand={result['summary']['wand_id']} "
        f"source_stroke_id={result['summary']['source_stroke_id']} "
        f"reported_attempt_id={result['summary']['reported_attempt_id']} "
        f"reported_points={result['summary']['reported_points']} "
        f"mode={result['summary']['mode']} "
        f"close_reason={result['summary']['close_reason']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"HTTP error: {exc.code} {exc.reason}")
        raise
