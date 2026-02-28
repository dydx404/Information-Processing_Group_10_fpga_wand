#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw
import math


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data" / "templates"
    out_dir.mkdir(parents=True, exist_ok=True)

    size = 256
    pad = 22
    stroke = 8

    # Circle
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    d.ellipse((pad, pad, size - pad, size - pad), outline=255, width=stroke)
    img.save(out_dir / "circle_v1.png")

    # Triangle
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    pts = [(size // 2, pad), (size - pad, size - pad), (pad, size - pad), (size // 2, pad)]
    d.line(pts, fill=255, width=stroke, joint="curve")
    img.save(out_dir / "triangle_v1.png")

    # Infinity
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    cx = size // 2
    cy = size // 2
    rx = 54
    ry = 40
    d.ellipse((cx - 2 * rx, cy - ry, cx, cy + ry), outline=255, width=stroke)
    d.ellipse((cx, cy - ry, cx + 2 * rx, cy + ry), outline=255, width=stroke)
    img.save(out_dir / "infinity_v1.png")

    # Heart
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
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
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
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

    print(f"templates written to {out_dir}")


if __name__ == "__main__":
    main()
