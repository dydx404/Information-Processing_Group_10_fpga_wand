from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from brain.render.rasterize import rasterize


def test_rasterize_duplicate_points_produces_nonempty_image() -> None:
    points = [
        (0.1, 0.1, 1000),
        (0.1, 0.1, 1001),
        (0.2, 0.2, 1002),
        (0.2, 0.2, 1003),
        (0.3, 0.3, 1004),
    ]

    img = rasterize(points, size=256, stroke=3)

    assert img.size == (256, 256)
    assert max(img.getdata()) > 0
