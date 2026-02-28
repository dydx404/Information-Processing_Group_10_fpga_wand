#!/usr/bin/env python3
"""
End-to-end smoke test for Wand-Brain:
TX (UDP wb-point-v1) -> parser/state -> API -> rendering image endpoint.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, List

WB_STRUCT = struct.Struct("<HBBHHIIhhI")
MAGIC = 0x5742
VERSION = 1
PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04
Q15_MAX = 32767


@dataclass
class AttemptExpectation:
    stroke_id: int
    expected_points: int
    rate_hz: float


def now_ms_u32() -> int:
    return int(time.time() * 1000) & 0xFFFFFFFF


def to_q15(v: float) -> int:
    return max(0, min(Q15_MAX, int(round(v * Q15_MAX))))


def parse_rates(raw: str) -> List[float]:
    rates: List[float] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        rates.append(float(part))
    if not rates:
        raise ValueError("at least one rate is required")
    return rates


def trajectory_point(i: int, n: int, pattern: str) -> tuple[float, float]:
    if n <= 1:
        return (0.5, 0.5)
    t = i / (n - 1)
    if pattern == "circle":
        a = 2.0 * math.pi * t
        return (0.5 + 0.45 * math.cos(a), 0.5 + 0.45 * math.sin(a))
    return (t, t)


def send_stroke(
    sock: socket.socket,
    host: str,
    port: int,
    *,
    device_number: int,
    wand_id: int,
    stroke_id: int,
    packet_number_start: int,
    rate_hz: float,
    duration_s: float,
    pattern: str,
) -> int:
    n_points = max(2, int(round(rate_hz * duration_s)))
    packet_number = packet_number_start
    start_monotonic = time.perf_counter()
    last_x_q = to_q15(0.5)
    last_y_q = to_q15(0.5)

    for i in range(n_points):
        target_t = start_monotonic + (i / rate_hz)
        while True:
            rem = target_t - time.perf_counter()
            if rem <= 0:
                break
            time.sleep(min(rem, 0.001))

        x, y = trajectory_point(i, n_points, pattern)
        x_q = to_q15(x)
        y_q = to_q15(y)
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
        sock.sendto(payload, (host, port))
        packet_number += 1
        last_x_q = x_q
        last_y_q = y_q

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
    sock.sendto(end_payload, (host, port))
    return packet_number + 1


def get_json(url: str, timeout_s: float = 5.0) -> Dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def get_bytes(url: str, timeout_s: float = 5.0) -> bytes:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read()


def wait_for_attempt(
    host: str,
    api_port: int,
    wand_id: int,
    expected_stroke_id: int,
    timeout_s: float,
) -> Dict:
    deadline = time.time() + timeout_s
    url = f"http://{host}:{api_port}/api/v1/attempt/latest?wand_id={wand_id}"
    last_error = ""
    while time.time() < deadline:
        try:
            data = get_json(url, timeout_s=3.0)
            got_id = int(data.get("attempt_id", -1))
            if got_id >= expected_stroke_id:
                return data
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(0.2)
    raise TimeoutError(
        f"timed out waiting for attempt {expected_stroke_id} on wand {wand_id}; last_error={last_error}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Full Wand-Brain TX->parser->API->render smoke test.")
    ap.add_argument("--host", default="127.0.0.1", help="Wand-Brain host/IP for UDP+HTTP")
    ap.add_argument("--udp-port", type=int, default=41000)
    ap.add_argument("--api-port", type=int, default=8000)
    ap.add_argument("--device", type=int, default=1)
    ap.add_argument("--wand", type=int, default=1)
    ap.add_argument("--stroke-start", type=int, default=int(time.time()) & 0x7FFFFFFF)
    ap.add_argument("--packet-start", type=int, default=0)
    ap.add_argument("--rates", default="25,50,100")
    ap.add_argument("--duration", type=float, default=2.0)
    ap.add_argument("--pause", type=float, default=0.4)
    ap.add_argument("--pattern", choices=["line", "circle"], default="line")
    ap.add_argument("--attempt-timeout", type=float, default=8.0)
    ap.add_argument(
        "--min-receive-ratio",
        type=float,
        default=0.85,
        help="minimum acceptable received_points/sent_points ratio for final attempt",
    )
    args = ap.parse_args()

    rates = parse_rates(args.rates)

    print(f"[1/5] Health check: http://{args.host}:{args.api_port}/api/v1/health")
    health = get_json(f"http://{args.host}:{args.api_port}/api/v1/health")
    if not health.get("ok"):
        print(f"FAIL: health response not ok: {health}")
        return 1
    print(f"      ok: service={health.get('service')} version={health.get('version')}")

    print(f"[2/5] Send UDP strokes to {args.host}:{args.udp_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_no = args.packet_start
    expectations: List[AttemptExpectation] = []
    stroke_id = args.stroke_start

    for i, rate in enumerate(rates, start=1):
        expected_points = max(2, int(round(rate * args.duration)))
        packet_no = send_stroke(
            sock,
            args.host,
            args.udp_port,
            device_number=args.device,
            wand_id=args.wand,
            stroke_id=stroke_id,
            packet_number_start=packet_no,
            rate_hz=rate,
            duration_s=args.duration,
            pattern=args.pattern,
        )
        expectations.append(
            AttemptExpectation(
                stroke_id=stroke_id,
                expected_points=expected_points,
                rate_hz=rate,
            )
        )
        print(f"      sent stroke {i}/{len(rates)}: stroke_id={stroke_id} rate={rate} pps points={expected_points}")
        stroke_id += 1
        if i != len(rates):
            time.sleep(max(0.0, args.pause))

    print("[3/5] Verify latest attempt via API")
    final_exp = expectations[-1]
    latest = wait_for_attempt(
        args.host, args.api_port, args.wand, final_exp.stroke_id, timeout_s=args.attempt_timeout
    )
    got_attempt = int(latest["attempt_id"])
    got_points = int(latest["num_points"])
    got_wand = int(latest["wand_id"])
    got_device = int(latest["device_number"])
    if got_attempt != final_exp.stroke_id:
        print(f"FAIL: latest attempt_id={got_attempt}, expected {final_exp.stroke_id}")
        return 2
    receive_ratio = got_points / final_exp.expected_points if final_exp.expected_points else 0.0
    if receive_ratio < args.min_receive_ratio:
        print(
            f"FAIL: num_points={got_points}, sent={final_exp.expected_points}, "
            f"receive_ratio={receive_ratio:.3f} < min {args.min_receive_ratio:.3f}"
        )
        return 3
    if got_wand != args.wand or got_device != args.device:
        print(
            f"FAIL: mismatch wand/device got wand={got_wand},device={got_device} "
            f"expected wand={args.wand},device={args.device}"
        )
        return 4
    print(
        f"      latest attempt OK: id={got_attempt} points={got_points}/{final_exp.expected_points} "
        f"(receive_ratio={receive_ratio:.3f})"
    )

    print("[4/5] Verify rendered image endpoint")
    image_url = f"http://{args.host}:{args.api_port}/api/v1/attempt/{got_attempt}/image.png"
    image_bytes = get_bytes(image_url)
    if len(image_bytes) == 0:
        print("FAIL: image endpoint returned empty body")
        return 5
    print(f"      image OK: {len(image_bytes)} bytes")

    print("[5/5] Verify wand status endpoint")
    wands = get_json(f"http://{args.host}:{args.api_port}/api/v1/wands")
    wand_items = wands.get("wands", [])
    target = next((w for w in wand_items if int(w.get("wand_id", -1)) == args.wand), None)
    if target is None:
        print(f"FAIL: wand {args.wand} missing from /api/v1/wands")
        return 6
    if target.get("last_point_ms") is None:
        print("FAIL: wand has null last_point_ms")
        return 7
    print(
        "      wand status OK: "
        f"active={target.get('active')} current_attempt_id={target.get('current_attempt_id')} "
        f"last_point_ms={target.get('last_point_ms')}"
    )

    print("\nPASS: full TX -> parser/state -> API -> render smoke test succeeded.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
        raise
