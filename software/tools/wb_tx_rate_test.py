#!/usr/bin/env python3
"""
wb-point-v1 UDP transmitter for rate testing (WSL/PYNQ/Jupyter friendly).
"""

from __future__ import annotations

import argparse
import math
import socket
import struct
import time
from dataclasses import dataclass
from typing import List

# wb-point-v1 packet: 24 bytes, little-endian
WB_STRUCT = struct.Struct("<HBBHHIIhhI")
MAGIC = 0x5742
VERSION = 1

PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04
Q15_MAX = 32767


@dataclass
class TxStats:
    rate_hz: float
    target_points: int
    sent_points: int
    duration_s: float
    achieved_pps: float
    mean_dt_ms: float


def now_ms_u32() -> int:
    return int(time.time() * 1000) & 0xFFFFFFFF


def to_q15(v: float) -> int:
    return max(0, min(Q15_MAX, int(round(v * Q15_MAX))))


def trajectory_point(i: int, n: int, pattern: str) -> tuple[float, float]:
    if n <= 1:
        return (0.5, 0.5)

    t = i / (n - 1)
    if pattern == "circle":
        # One full circle centered at (0.5, 0.5), radius 0.45
        a = 2.0 * math.pi * t
        return (0.5 + 0.45 * math.cos(a), 0.5 + 0.45 * math.sin(a))
    # Default: diagonal line
    return (t, t)


def parse_rates(raw: str | None, fallback: float) -> List[float]:
    if not raw:
        return [fallback]
    rates: List[float] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        rates.append(float(part))
    return rates


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
) -> tuple[int, TxStats]:
    if rate_hz <= 0:
        raise ValueError("rate_hz must be > 0")
    if duration_s <= 0:
        raise ValueError("duration_s must be > 0")

    n_points = max(2, int(round(rate_hz * duration_s)))
    packet_number = packet_number_start
    send_times: List[float] = []

    start_monotonic = time.perf_counter()
    last_x_q = to_q15(0.5)
    last_y_q = to_q15(0.5)

    for i in range(n_points):
        target_t = start_monotonic + (i / rate_hz)
        while True:
            now = time.perf_counter()
            remaining = target_t - now
            if remaining <= 0:
                break
            time.sleep(min(remaining, 0.001))

        x, y = trajectory_point(i, n_points, pattern=pattern)
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
        send_times.append(time.perf_counter())

        last_x_q = x_q
        last_y_q = y_q
        packet_number += 1

    # Final protocol packet with STROKE_END and PEN_DOWN=0.
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
    packet_number += 1

    elapsed_s = max(send_times[-1] - send_times[0], 1e-9) if len(send_times) > 1 else 1e-9
    achieved_pps = (len(send_times) - 1) / elapsed_s if len(send_times) > 1 else 0.0

    mean_dt_ms = 0.0
    if len(send_times) > 1:
        dts = [(send_times[i] - send_times[i - 1]) * 1000.0 for i in range(1, len(send_times))]
        mean_dt_ms = sum(dts) / len(dts)

    stats = TxStats(
        rate_hz=rate_hz,
        target_points=n_points,
        sent_points=n_points,
        duration_s=duration_s,
        achieved_pps=achieved_pps,
        mean_dt_ms=mean_dt_ms,
    )
    return packet_number, stats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Send wb-point-v1 UDP packets at controlled rates.")
    p.add_argument("--host", default="127.0.0.1", help="Wand-Brain host/IP")
    p.add_argument("--port", type=int, default=41000, help="Wand-Brain UDP port")
    p.add_argument("--device", type=int, default=1, help="device_number")
    p.add_argument("--wand", type=int, default=1, help="wand_id")
    p.add_argument("--stroke-start", type=int, default=1000, help="initial stroke_id")
    p.add_argument("--packet-start", type=int, default=0, help="initial packet_number")
    p.add_argument("--rate", type=float, default=50.0, help="single test rate (packets/sec)")
    p.add_argument(
        "--sweep",
        default="25,50,100",
        help="comma-separated rates to test (overrides --rate)",
    )
    p.add_argument("--duration", type=float, default=8.0, help="seconds per rate")
    p.add_argument("--pause", type=float, default=0.5, help="seconds between rates")
    p.add_argument("--repeat", type=int, default=1, help="repeat whole rate sweep N times")
    p.add_argument("--pattern", choices=["line", "circle"], default="line")
    return p


def main() -> None:
    args = build_parser().parse_args()
    rates = parse_rates(args.sweep, args.rate)
    if not rates:
        rates = [args.rate]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_number = args.packet_start
    stroke_id = args.stroke_start

    print(f"Target: {args.host}:{args.port} device={args.device} wand={args.wand}")
    print(
        f"Rates: {rates} pps, duration={args.duration}s each, "
        f"repeat={args.repeat}, pattern={args.pattern}"
    )

    total_steps = len(rates) * max(1, args.repeat)
    step = 0
    for rep in range(max(1, args.repeat)):
        for idx, rate in enumerate(rates):
            step += 1
            packet_number, stats = send_stroke(
                sock,
                args.host,
                args.port,
                device_number=args.device,
                wand_id=args.wand,
                stroke_id=stroke_id,
                packet_number_start=packet_number,
                rate_hz=rate,
                duration_s=args.duration,
                pattern=args.pattern,
            )
            print(
                f"[{step}/{total_steps}] stroke_id={stroke_id} "
                f"rate={stats.rate_hz:.1f} pps sent={stats.sent_points} "
                f"achieved~{stats.achieved_pps:.2f} pps mean_dt={stats.mean_dt_ms:.2f} ms"
            )
            stroke_id += 1
            if not (rep == args.repeat - 1 and idx == len(rates) - 1):
                time.sleep(max(0.0, args.pause))

    print("Done.")


if __name__ == "__main__":
    main()
