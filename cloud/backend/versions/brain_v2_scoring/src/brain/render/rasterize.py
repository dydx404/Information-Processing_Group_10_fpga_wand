from __future__ import annotations
from typing import List, Tuple
import math
import numpy as np
from PIL import Image, ImageDraw

Point = Tuple[float, float, int]  # (x, y, t)

def _normalize_xy(points: List[Point], size: int, margin: int = 10):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    w = maxx - minx
    h = maxy - miny
    if w == 0 and h == 0:
        # all points identical: put in center
        return [(size // 2, size // 2) for _ in points]

    # scale to fit canvas with margin, keep aspect ratio
    span = max(w, h)
    scale = (size - 2 * margin) / span if span > 0 else 1.0

    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0

    out = []
    for x, y, _t in points:
        nx = (x - cx) * scale + size / 2.0
        ny = (y - cy) * scale + size / 2.0
        out.append((int(round(nx)), int(round(ny))))
    return out

def rasterize(points: List[Point], size: int = 256, stroke: int = 3) -> Image.Image:
    """
    Returns a grayscale PIL image (L mode) with white stroke on black background.
    """
    img = Image.new("L", (size, size), 0)
    if not points:
        return img

    xy = _normalize_xy(points, size=size, margin=10)
    draw = ImageDraw.Draw(img)

    if len(xy) == 1:
        x, y = xy[0]
        r = max(1, stroke)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=255)
        return img

    # draw polyline
    draw.line(xy, fill=255, width=stroke, joint="curve")
    return img
