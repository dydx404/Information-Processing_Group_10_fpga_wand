#!/usr/bin/env python3
"""
Long single-stroke wb-point-v1 transmitter with configurable noise and shape.
Designed to mimic one full button-hold drawing attempt.
"""

from __future__ import annotations

import argparse
import math
import random
import socket
import struct
import time

# wb-point-v1: 24 bytes, little-endian
WB_STRUCT = struct.Struct("<HBBHHIIhhI")
MAGIC = 0x5742
VERSION = 1

PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04
Q15_MAX = 32767


def now_ms_u32() -> int:
    return int(time.time() * 1000) & 0xFFFFFFFF


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def to_q15(v: float) -> int:
    return int(round(clamp01(v) * Q15_MAX))


def base_point(t: float, shape: str) -> tuple[float, float]:
    """
    t in [0, 1]
    Returns normalized x,y in [0,1] before noise.
    """
    if shape == "spiral":
        # Outward spiral centered at 0.5,0.5
        turns = 2.2
        ang = 2.0 * math.pi * turns * t
        r = 0.08 + 0.38 * t
        return 0.5 + r * math.cos(ang), 0.5 + r * math.sin(ang)

    if shape == "lemniscate":
        # Figure-eight / infinity style curve
        ang = 2.0 * math.pi * t
        a = 0.38
        x = a * math.sin(ang)
        y = a * math.sin(ang) * math.cos(ang)
        return 0.5 + x, 0.5 + y

    if shape == "lissajous":
        # Smooth "spell-like" curve
        ang = 2.0 * math.pi * t
        x = 0.38 * math.sin(3.0 * ang + math.pi / 2.0)
        y = 0.38 * math.sin(2.0 * ang)
        return 0.5 + x, 0.5 + y

    if shape == "heart":
        # Parametric heart, matched to template orientation/scale.
        ang = (2.0 * math.pi) * t
        x = 16 * (math.sin(ang) ** 3)
        y = (
            13 * math.cos(ang)
            - 5 * math.cos(2 * ang)
            - 2 * math.cos(3 * ang)
            - math.cos(4 * ang)
        )
        nx = 0.5 + (x / 18.0) * 0.38
        ny = 0.5 - ((y - 2.0) / 18.0) * 0.38
        return nx, ny

    # default: slow circle
    ang = 2.0 * math.pi * t
    return 0.5 + 0.42 * math.cos(ang), 0.5 + 0.42 * math.sin(ang)


def noisy_point(t: float, shape: str, noise_std: float, wander_std: float, drift: tuple[float, float]) -> tuple[float, float]:
    x, y = base_point(t, shape)

    # Gaussian point jitter (simulates centroid noise)
    if noise_std > 0:
        x += random.gauss(0.0, noise_std)
        y += random.gauss(0.0, noise_std)

    # Low-frequency wander (camera/system drift-like)
    if wander_std > 0:
        x += random.gauss(0.0, wander_std)
        y += random.gauss(0.0, wander_std)

    # Tiny linear drift over stroke
    x += drift[0] * t
    y += drift[1] * t

    return clamp01(x), clamp01(y)


def send_long_stroke(
    host: str,
    port: int,
    *,
    device_number: int,
    wand_id: int,
    stroke_id: int,
    packet_number_start: int,
    rate_hz: float,
    duration_s: float,
    shape: str,
    noise_std: float,
    wander_std: float,
    drift_x: float,
    drift_y: float,
) -> tuple[int, int]:
    if rate_hz <= 0 or duration_s <= 0:
        raise ValueError("rate_hz and duration_s must be > 0")

    n_points = max(2, int(round(rate_hz * duration_s)))
    packet_number = packet_number_start
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    start = time.perf_counter()
    last_x_q, last_y_q = to_q15(0.5), to_q15(0.5)

    for i in range(n_points):
        target_t = start + (i / rate_hz)
        while True:
            rem = target_t - time.perf_counter()
            if rem <= 0:
                break
            time.sleep(min(rem, 0.001))

        t = i / (n_points - 1)
        x, y = noisy_point(
            t,
            shape=shape,
            noise_std=noise_std,
            wander_std=wander_std,
            drift=(drift_x, drift_y),
        )
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
        last_x_q, last_y_q = x_q, y_q

    # Final packet closes the one long button-hold attempt.
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
    sock.close()
    return n_points, packet_number


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Send one long noisy wb-point-v1 stroke.")
    p.add_argument("--host", default="127.0.0.1", help="Wand-Brain host/IP")
    p.add_argument("--port", type=int, default=41000, help="Wand-Brain UDP port")
    p.add_argument("--device", type=int, default=1, help="device_number")
    p.add_argument("--wand", type=int, default=1, help="wand_id")
    p.add_argument("--stroke-id", type=int, default=777777, help="single stroke_id for this long attempt")
    p.add_argument("--packet-start", type=int, default=0, help="initial packet_number")
    p.add_argument("--rate", type=float, default=20.0, help="packets per second (slow drawing)")
    p.add_argument("--duration", type=float, default=30.0, help="seconds (long button-hold)")
    p.add_argument(
        "--shape",
        choices=["circle", "spiral", "lemniscate", "lissajous", "heart"],
        default="heart",
        help="trajectory shape",
    )
    p.add_argument("--noise-std", type=float, default=0.006, help="fast gaussian jitter std in normalized units")
    p.add_argument("--wander-std", type=float, default=0.002, help="slow wander noise std in normalized units")
    p.add_argument("--drift-x", type=float, default=0.0, help="small linear x drift over whole stroke")
    p.add_argument("--drift-y", type=float, default=0.0, help="small linear y drift over whole stroke")
    p.add_argument("--seed", type=int, default=42, help="RNG seed for repeatability")
    return p


def main() -> None:
    args = build_parser().parse_args()
    random.seed(args.seed)

    print(
        f"TX long stroke -> {args.host}:{args.port} "
        f"device={args.device} wand={args.wand} stroke_id={args.stroke_id}"
    )
    print(
        f"shape={args.shape} rate={args.rate} pps duration={args.duration}s "
        f"noise_std={args.noise_std} wander_std={args.wander_std}"
    )

    start = time.perf_counter()
    sent_points, next_pkt = send_long_stroke(
        args.host,
        args.port,
        device_number=args.device,
        wand_id=args.wand,
        stroke_id=args.stroke_id,
        packet_number_start=args.packet_start,
        rate_hz=args.rate,
        duration_s=args.duration,
        shape=args.shape,
        noise_std=args.noise_std,
        wander_std=args.wander_std,
        drift_x=args.drift_x,
        drift_y=args.drift_y,
    )
    elapsed = time.perf_counter() - start
    print(
        f"Done. sent_points={sent_points} elapsed={elapsed:.2f}s "
        f"next_packet_number={next_pkt}"
    )


if __name__ == "__main__":
    main()
