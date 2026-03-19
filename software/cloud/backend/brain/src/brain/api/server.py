from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
from pathlib import Path as FSPath
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import os
import time

from brain.ingest.udp_rx import UdpReceiver
from brain.ingest.parser import parse_packet, PointEvent
from brain.render.rasterize import rasterize

# ----------------------------
# App + constants
# ----------------------------
app = FastAPI(title="FPGA-Wand Brain", version="0.1.0")

SERVICE_NAME = "wand-brain"
SERVICE_VERSION = "0.1.0"

OUTDIR = FSPath("data/outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)

Point = Tuple[float, float, int]  # (x, y, timestamp_ms)

# ----------------------------
# Models
# ----------------------------
@dataclass
class AttemptBuffer:
    points: List[Point] = field(default_factory=list)
    last_live_render_ms: int = 0

@dataclass
class FinalResult:
    device_number: int
    wand_id: int
    attempt_id: int  # == stroke_id in UDP for MVP
    num_points: int
    start_ms: int
    end_ms: int
    finalized_at_ms: int
    render_path: str
    # scoring placeholders (wire later)
    status: str = "processed"
    best_template_id: Optional[str] = None
    best_template_name: Optional[str] = None
    score: Optional[float] = None

@dataclass
class WandStatus:
    wand_id: int
    active: bool
    current_attempt_id: Optional[int]
    last_point_ms: Optional[int]

class BrainState:
    def __init__(self):
        # key: (device, wand, attempt_id)
        self.attempts: Dict[tuple[int, int, int], AttemptBuffer] = {}
        # latest finalized per (device, wand)
        self.last_result: Dict[tuple[int, int], FinalResult] = {}
        # index for image lookup by (wand_id, attempt_id) for MVP web API
        self.attempt_index: Dict[int, FinalResult] = {}
        # live status per wand_id (MVP assumes wand_id unique in system)
        self.wand_status: Dict[int, WandStatus] = {}
        # latest live-rendered path per wand_id while attempt is active
        self.live_render_path: Dict[int, str] = {}
        self.last_event: Optional[PointEvent] = None

    def _ensure_wand(self, wand_id: int) -> WandStatus:
        ws = self.wand_status.get(wand_id)
        if ws is None:
            ws = WandStatus(wand_id=wand_id, active=False, current_attempt_id=None, last_point_ms=None)
            self.wand_status[wand_id] = ws
        return ws

    def on_event(self, ev: PointEvent):
        self.last_event = ev

        ws = self._ensure_wand(ev.wand_id)
        ws.last_point_ms = ev.timestamp_ms

        # Active attempt bookkeeping (button hold)
        if ev.pen_down:
            ws.active = True
            ws.current_attempt_id = ev.stroke_id
            self._add_point(ev)
        else:
            # if pen is up but we haven't ended, don't force inactive (END packet will close)
            pass

        # End marker finalizes attempt
        if ev.stroke_end:
            ws.active = False
            ws.current_attempt_id = None
            self._finalize(ev.device_number, ev.wand_id, ev.stroke_id)

    def _add_point(self, ev: PointEvent):
        key = (ev.device_number, ev.wand_id, ev.stroke_id)
        buf = self.attempts.setdefault(key, AttemptBuffer())
        buf.points.append((ev.x, ev.y, ev.timestamp_ms))
        if len(buf.points) > 5000:
            buf.points = buf.points[-5000:]
        self._render_live_if_due(ev.wand_id, buf)

    def _render_live_if_due(self, wand_id: int, buf: AttemptBuffer, interval_ms: int = 80):
        now_ms = int(time.time() * 1000)
        # Render first point quickly, then throttle to avoid excessive I/O.
        if buf.last_live_render_ms and (now_ms - buf.last_live_render_ms) < interval_ms:
            return
        img = rasterize(buf.points, size=256, stroke=3)
        live_path = OUTDIR / f"wand_{wand_id}_live.png"
        tmp_path = OUTDIR / f".wand_{wand_id}_live.tmp.png"
        img.save(tmp_path)
        os.replace(tmp_path, live_path)
        self.live_render_path[wand_id] = str(live_path)
        buf.last_live_render_ms = now_ms

    def _finalize(self, device: int, wand: int, attempt_id: int) -> Optional[FinalResult]:
        key = (device, wand, attempt_id)
        buf = self.attempts.get(key)
        if buf is None or not buf.points:
            self.attempts.pop(key, None)
            return None

        pts = buf.points
        start_ms = pts[0][2]
        end_ms = pts[-1][2]
        finalized_at_ms = int(time.time() * 1000)

        img = rasterize(pts, size=256, stroke=3)
        out_path = OUTDIR / f"dev{device}_wand{wand}_attempt{attempt_id}_{finalized_at_ms}.png"
        img.save(out_path)

        res = FinalResult(
            device_number=device,
            wand_id=wand,
            attempt_id=attempt_id,
            num_points=len(pts),
            start_ms=start_ms,
            end_ms=end_ms,
            finalized_at_ms=finalized_at_ms,
            render_path=str(out_path),
        )

        self.last_result[(device, wand)] = res
        self.attempt_index[attempt_id] = res  # MVP lookup by wand+attempt
        self.live_render_path[wand] = str(out_path)
        self.attempts.pop(key, None)
        return res

    def snapshot(self):
        return {
            "attempt_buffer_sizes": {str(k): len(v.points) for k, v in self.attempts.items()},
            "last_event": None if self.last_event is None else self.last_event.__dict__,
            "last_result_keys": [f"{k[0]},{k[1]}" for k in self.last_result.keys()],
            "wands": {str(k): self.wand_status[k].__dict__ for k in self.wand_status},
        }

state = BrainState()

def on_udp_packet(raw: bytes, addr):
    ev = parse_packet(raw)
    if ev is None:
        return
    state.on_event(ev)

udp = UdpReceiver(host="0.0.0.0", port=41000, on_packet=on_udp_packet)

@app.on_event("startup")
def _startup():
    udp.start()

# ----------------------------
# Existing endpoints (dev)
# ----------------------------
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/debug/state")
def debug_state():
    return state.snapshot()

# ----------------------------
# WEB CONTRACT: /api/v1/* (exact 5)
# ----------------------------

# 1) /api/v1/health
@app.get("/api/v1/health")
def api_health():
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "time_ms": int(time.time() * 1000),
    }

# 2) /api/v1/wands
@app.get("/api/v1/wands")
def api_wands():
    now_ms = int(time.time() * 1000)
    return {
        "time_ms": now_ms,
        "wands": [ws.__dict__ for ws in state.wand_status.values()],
    }

# 3) /api/v1/wand/{wand_id}
@app.get("/api/v1/wand/{wand_id}")
def api_wand(wand_id: int = Path(..., ge=1)):
    ws = state.wand_status.get(wand_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="wand not found")
    return ws.__dict__

def _attempt_result_payload(res: FinalResult):
    return {
        "attempt_id": res.attempt_id,
        "wand_id": res.wand_id,
        "device_number": res.device_number,
        "start_ms": res.start_ms,
        "end_ms": res.end_ms,
        "num_points": res.num_points,
        "result": {
            "status": res.status,
            "best_template_id": res.best_template_id,
            "best_template_name": res.best_template_name,
            "score": res.score,
        },
        "image_png": f"/api/v1/attempt/{res.attempt_id}/image.png",
    }

# 4) /api/v1/attempt/latest?wand_id=
@app.get("/api/v1/attempt/latest")
def api_attempt_latest(wand_id: int = Query(..., ge=1)):
    # MVP: find latest attempt for this wand by scanning last_result values
    candidates = [r for r in state.last_result.values() if r.wand_id == wand_id]
    if not candidates:
        raise HTTPException(status_code=404, detail="no attempt yet for this wand")
    # choose newest by finalized_at_ms
    res = max(candidates, key=lambda r: r.finalized_at_ms)
    return _attempt_result_payload(res)

# 5) /api/v1/attempt/{attempt_id}/image.png
@app.api_route("/api/v1/attempt/{attempt_id}/image.png", methods=["GET", "HEAD"])
def api_attempt_image(
    attempt_id: int = Path(..., ge=0),):
    res = state.attempt_index.get(attempt_id)
    if res is None:
        raise HTTPException(status_code=404, detail="attempt image not found")
    resp = FileResponse(res.render_path, media_type="image/png")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.api_route("/api/v1/wand/{wand_id}/live.png", methods=["GET", "HEAD"])
def api_wand_live_image(wand_id: int = Path(..., ge=1)):
    render_path = state.live_render_path.get(wand_id)
    if not render_path:
        # Fallback: serve latest finalized attempt for this wand if available.
        candidates = [r for r in state.last_result.values() if r.wand_id == wand_id]
        if not candidates:
            raise HTTPException(status_code=404, detail="no live image for this wand")
        render_path = max(candidates, key=lambda r: r.finalized_at_ms).render_path
    resp = FileResponse(render_path, media_type="image/png")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp
