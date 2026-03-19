#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw
import math


def fit_points(points, size: int, pad: int) -> list[tuple[float, float]]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    span_x = max(1e-9, max_x - min_x)
    span_y = max(1e-9, max_y - min_y)
    scale = min((size - 2 * pad) / span_x, (size - 2 * pad) / span_y)

    offset_x = (size - span_x * scale) / 2.0
    offset_y = (size - span_y * scale) / 2.0

    return [
        ((x - min_x) * scale + offset_x, (y - min_y) * scale + offset_y)
        for (x, y) in points
    ]


def new_canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("L", (size, size), 0)
    return img, ImageDraw.Draw(img)


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data" / "templates"
    out_dir.mkdir(parents=True, exist_ok=True)

    size = 256
    pad = 22
    stroke = 8

    # Circle
    img, d = new_canvas(size)
    d.ellipse((pad, pad, size - pad, size - pad), outline=255, width=stroke)
    img.save(out_dir / "circle_v1.png")

    # Triangle
    img, d = new_canvas(size)
    pts = [(size // 2, pad), (size - pad, size - pad), (pad, size - pad), (size // 2, pad)]
    d.line(pts, fill=255, width=stroke, joint="curve")
    img.save(out_dir / "triangle_v1.png")

    # Infinity
    img, d = new_canvas(size)
    cx = size // 2
    cy = size // 2
    rx = 54
    ry = 40
    d.ellipse((cx - 2 * rx, cy - ry, cx, cy + ry), outline=255, width=stroke)
    d.ellipse((cx, cy - ry, cx + 2 * rx, cy + ry), outline=255, width=stroke)
    img.save(out_dir / "infinity_v1.png")

    # Heart
    img, d = new_canvas(size)
    pts = []
    # Parametric heart scaled into the canvas.
    for i in range(420):
        t = (2.0 * math.pi) * (i / 419.0)
        x = 16 * (math.sin(t) ** 3)
        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )
        # Normalize approximately to fit.
        nx = size / 2 + (x / 18.0) * (size * 0.38)
        ny = size / 2 - ((y - 2.0) / 18.0) * (size * 0.38)
        pts.append((nx, ny))
    d.line(pts, fill=255, width=stroke, joint="curve")
    img.save(out_dir / "heart_v1.png")

    # Sine wave
    img, d = new_canvas(size)
    pts = []
    left = pad
    right = size - pad
    for i in range(420):
        t = i / 419.0
        x = left + t * (right - left)
        # 1.75 cycles, centered vertically.
        y = size / 2 - (size * 0.23) * math.sin(2.0 * math.pi * 1.75 * t)
        pts.append((x, y))
    d.line(pts, fill=255, width=stroke, joint="curve")
    img.save(out_dir / "sine_v1.png")

    # Golden curve
    img, d = new_canvas(size)
    pts = []
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    theta_start = -0.25 * math.pi
    theta_end = 2.15 * math.pi
    for i in range(520):
        t = i / 519.0
        theta = theta_start + (theta_end - theta_start) * t
        radius = phi ** ((2.0 * theta) / math.pi)
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        pts.append((x, y))
    d.line(fit_points(pts, size, pad + 6), fill=255, width=stroke, joint="curve")
    img.save(out_dir / "golden_curve_v1.png")

    # Clover
    img, d = new_canvas(size)
    pts = []
    for i in range(720):
        theta = (2.0 * math.pi) * (i / 719.0)
        radius = math.cos(2.0 * theta)
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        pts.append((x, y))
    d.line(fit_points(pts, size, pad + 8), fill=255, width=stroke, joint="curve")
    img.save(out_dir / "clover_v1.png")

    # Star
    img, d = new_canvas(size)
    pts = []
    outer_r = (size / 2) - pad
    inner_r = outer_r * 0.42
    cx = size / 2
    cy = size / 2
    for i in range(10):
        angle = -math.pi / 2 + i * (math.pi / 5)
        radius = outer_r if (i % 2 == 0) else inner_r
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    pts.append(pts[0])
    d.line(pts, fill=255, width=stroke, joint="curve")
    img.save(out_dir / "star_v1.png")

    print(f"templates written to {out_dir}")


if __name__ == "__main__":
    main()
