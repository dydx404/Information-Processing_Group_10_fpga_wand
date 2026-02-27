from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PIL import Image


@dataclass
class TemplateRef:
    template_id: str
    name: str
    path: str


@dataclass
class ScoreResult:
    template_id: str
    template_name: str
    score: float
    metrics: dict


def list_templates(template_dir: Path) -> list[TemplateRef]:
    if not template_dir.exists():
        return []
    items: list[TemplateRef] = []
    for p in sorted(template_dir.glob("*.png")):
        tid = p.stem
        items.append(TemplateRef(template_id=tid, name=tid.replace("_", " ").title(), path=str(p)))
    return items


def _to_bin(path: Path, size: int = 256, threshold: int = 10) -> Image.Image:
    # Low threshold keeps thin strokes visible.
    img = Image.open(path).convert("L").resize((size, size))
    return img.point(lambda px: 255 if px > threshold else 0, mode="1")


def _count_on(img_bin: Image.Image) -> int:
    # In mode "1", pixels are 0/255.
    return sum(1 for v in img_bin.getdata() if v)


def _intersection_and_union(a: Image.Image, b: Image.Image) -> tuple[int, int]:
    ad = a.getdata()
    bd = b.getdata()
    inter = 0
    union = 0
    for pa, pb in zip(ad, bd):
        oa = bool(pa)
        ob = bool(pb)
        if oa and ob:
            inter += 1
        if oa or ob:
            union += 1
    return inter, union


def compute_score(drawing_path: Path, template_path: Path) -> ScoreResult:
    draw_bin = _to_bin(drawing_path)
    tmpl_bin = _to_bin(template_path)

    draw_on = _count_on(draw_bin)
    tmpl_on = _count_on(tmpl_bin)
    inter, union = _intersection_and_union(draw_bin, tmpl_bin)

    iou = (inter / union) if union else 0.0
    dice = (2.0 * inter / (draw_on + tmpl_on)) if (draw_on + tmpl_on) else 0.0
    area_ratio = (min(draw_on, tmpl_on) / max(draw_on, tmpl_on)) if max(draw_on, tmpl_on) else 0.0

    # Weighted composite score, 0..100.
    score = 100.0 * (0.55 * dice + 0.35 * iou + 0.10 * area_ratio)

    template_id = template_path.stem
    return ScoreResult(
        template_id=template_id,
        template_name=template_id.replace("_", " ").title(),
        score=round(score, 3),
        metrics={
            "dice": round(dice, 4),
            "iou": round(iou, 4),
            "area_ratio": round(area_ratio, 4),
            "draw_pixels_on": draw_on,
            "template_pixels_on": tmpl_on,
            "intersection_pixels": inter,
            "union_pixels": union,
        },
    )

