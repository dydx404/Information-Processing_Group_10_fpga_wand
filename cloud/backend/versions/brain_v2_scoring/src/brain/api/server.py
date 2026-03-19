from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path as FSPath
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import os
import threading
import time

from brain.ingest.udp_rx import UdpReceiver
from brain.ingest.parser import parse_packet, PointEvent
from brain.render.rasterize import rasterize
from brain.scoring import list_templates, compute_score

# ----------------------------
# App + constants
# ----------------------------
app = FastAPI(title="FPGA-Wand Brain", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_NAME = "wand-brain"
SERVICE_VERSION = "0.1.0"
IDLE_FINALIZE_MS = max(250, int(os.getenv("WB_IDLE_FINALIZE_MS", "1500")))
IDLE_SWEEP_INTERVAL_MS = max(50, int(os.getenv("WB_IDLE_SWEEP_INTERVAL_MS", "120")))
INTERNAL_ATTEMPT_ID_BASE = max(1_000_000_000, int(os.getenv("WB_ATTEMPT_ID_BASE", "1000000000")))
MIN_POINTS_TO_KEEP = max(1, int(os.getenv("WB_MIN_POINTS_TO_KEEP", "2")))

OUTDIR = FSPath("data/outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = FSPath("data/templates")
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

Point = Tuple[float, float, int]  # (x, y, timestamp_ms)

# ----------------------------
# Models
# ----------------------------
@dataclass
class AttemptBuffer:
    points: List[Point] = field(default_factory=list)
    last_live_render_ms: int = 0
    last_arrival_ms: int = 0
    source_stroke_id: int = 0

@dataclass
class FinalResult:
    device_number: int
    wand_id: int
    attempt_id: int
    source_stroke_id: int
    num_points: int
    start_ms: int
    end_ms: int
    finalized_at_ms: int
    render_path: str
    close_reason: str
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
    device_number: Optional[int] = None
    current_source_stroke_id: Optional[int] = None
    current_start_ms: Optional[int] = None
    current_points: int = 0
    last_finalized_attempt_id: Optional[int] = None
    last_close_reason: Optional[str] = None
    last_stroke_duration_ms: Optional[int] = None

class BrainState:
    def __init__(self):
        self.lock = threading.RLock()
        self.idle_finalize_ms = IDLE_FINALIZE_MS
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
        self._attempt_counter = INTERNAL_ATTEMPT_ID_BASE - 1

    def _ensure_wand(self, device_number: int, wand_id: int) -> WandStatus:
        ws = self.wand_status.get(wand_id)
        if ws is None:
            ws = WandStatus(
                wand_id=wand_id,
                active=False,
                current_attempt_id=None,
                last_point_ms=None,
                device_number=device_number,
            )
            self.wand_status[wand_id] = ws
        else:
            ws.device_number = device_number
        return ws

    def _next_attempt_id(self) -> int:
        self._attempt_counter += 1
        return self._attempt_counter

    def _resolve_attempt_id(self, ws: WandStatus, ev: PointEvent) -> int:
        source_stroke_id = ev.stroke_id or None

        if (
            ws.active
            and ws.current_attempt_id is not None
            and ws.device_number == ev.device_number
        ):
            if source_stroke_id is None:
                return ws.current_attempt_id
            if ws.current_source_stroke_id is None or ws.current_source_stroke_id == source_stroke_id:
                return ws.current_attempt_id

        return self._next_attempt_id()

    def on_event(self, ev: PointEvent):
        now_ms = int(time.time() * 1000)
        with self.lock:
            self._finalize_idle_attempts_locked(now_ms)
            self.last_event = ev

            ws = self._ensure_wand(ev.device_number, ev.wand_id)
            ws.last_point_ms = ev.timestamp_ms

            # For real PYNQ visibility mode, every non-pure-END packet is a point.
            # This keeps Brain usable even if PYNQ only knows "blob visible now".
            point_like = (not ev.stroke_end) or ev.pen_down or ev.stroke_start

            if point_like:
                attempt_id = self._resolve_attempt_id(ws, ev)

                if ws.active and ws.current_attempt_id is not None and ws.current_attempt_id != attempt_id:
                    self._finalize_locked(
                        ws.device_number or ev.device_number,
                        ev.wand_id,
                        ws.current_attempt_id,
                        close_reason="attempt_replaced",
                    )

                ws.active = True
                ws.current_attempt_id = attempt_id
                ws.current_source_stroke_id = ev.stroke_id or None
                self._add_point_locked(ev, attempt_id=attempt_id, arrival_ms=now_ms)

            if ev.stroke_end:
                attempt_id = ws.current_attempt_id
                if attempt_id is not None:
                    self._finalize_locked(
                        ev.device_number,
                        ev.wand_id,
                        attempt_id,
                        close_reason="explicit_end",
                    )

    def _add_point_locked(self, ev: PointEvent, attempt_id: int, arrival_ms: int):
        key = (ev.device_number, ev.wand_id, attempt_id)
        buf = self.attempts.setdefault(key, AttemptBuffer())
        buf.points.append((ev.x, ev.y, ev.timestamp_ms))
        buf.last_arrival_ms = arrival_ms
        if ev.stroke_id:
            buf.source_stroke_id = ev.stroke_id
        if len(buf.points) > 5000:
            buf.points = buf.points[-5000:]
        ws = self.wand_status.get(ev.wand_id)
        if ws is not None:
            if len(buf.points) == 1:
                ws.current_start_ms = ev.timestamp_ms
            ws.current_points = len(buf.points)
        self._render_live_if_due(ev.wand_id, buf)

    def _render_live_if_due(self, wand_id: int, buf: AttemptBuffer, interval_ms: int = 80):
        now_ms = int(time.time() * 1000)
        # Render first point quickly, then throttle to avoid excessive I/O.
        if buf.last_live_render_ms and (now_ms - buf.last_live_render_ms) < interval_ms:
            return
        img = rasterize(buf.points, size=256, stroke=3, normalize_view=False)
        live_path = OUTDIR / f"wand_{wand_id}_live.png"
        tmp_path = OUTDIR / f".wand_{wand_id}_live.tmp.png"
        img.save(tmp_path)
        os.replace(tmp_path, live_path)
        self.live_render_path[wand_id] = str(live_path)
        buf.last_live_render_ms = now_ms

    def _finalize_locked(
        self,
        device: int,
        wand: int,
        attempt_id: int,
        close_reason: str,
    ) -> Optional[FinalResult]:
        key = (device, wand, attempt_id)
        buf = self.attempts.get(key)
        if buf is None or not buf.points:
            self.attempts.pop(key, None)
            ws = self.wand_status.get(wand)
            if ws is not None and ws.current_attempt_id == attempt_id:
                ws.active = False
                ws.current_attempt_id = None
                ws.current_source_stroke_id = None
                ws.current_start_ms = None
                ws.current_points = 0
                ws.last_finalized_attempt_id = attempt_id
                ws.last_close_reason = close_reason
            return None

        pts = buf.points
        if len(pts) < MIN_POINTS_TO_KEEP and close_reason != "explicit_end":
            self.attempts.pop(key, None)
            ws = self.wand_status.get(wand)
            if ws is not None and ws.current_attempt_id == attempt_id:
                ws.active = False
                ws.current_attempt_id = None
                ws.current_source_stroke_id = None
                ws.current_start_ms = None
                ws.current_points = 0
                ws.last_finalized_attempt_id = attempt_id
                ws.last_close_reason = f"{close_reason}_discarded"
            return None

        start_ms = pts[0][2]
        end_ms = pts[-1][2]
        finalized_at_ms = int(time.time() * 1000)

        img = rasterize(pts, size=256, stroke=3, normalize_view=False)
        out_path = OUTDIR / f"dev{device}_wand{wand}_attempt{attempt_id}_{finalized_at_ms}.png"
        img.save(out_path)

        res = FinalResult(
            device_number=device,
            wand_id=wand,
            attempt_id=attempt_id,
            source_stroke_id=buf.source_stroke_id,
            num_points=len(pts),
            start_ms=start_ms,
            end_ms=end_ms,
            finalized_at_ms=finalized_at_ms,
            render_path=str(out_path),
            close_reason=close_reason,
        )

        self.last_result[(device, wand)] = res
        self.attempt_index[attempt_id] = res  # MVP lookup by wand+attempt
        self.live_render_path[wand] = str(out_path)
        self.attempts.pop(key, None)
        ws = self.wand_status.get(wand)
        if ws is not None and ws.current_attempt_id == attempt_id:
            ws.active = False
            ws.current_attempt_id = None
            ws.current_source_stroke_id = None
            ws.current_start_ms = None
            ws.current_points = 0
            ws.last_finalized_attempt_id = attempt_id
            ws.last_close_reason = close_reason
            ws.last_stroke_duration_ms = max(0, end_ms - start_ms)
        return res

    def _finalize_idle_attempts_locked(self, now_ms: int):
        for wand_id, ws in list(self.wand_status.items()):
            if not ws.active or ws.current_attempt_id is None or ws.device_number is None:
                continue

            key = (ws.device_number, wand_id, ws.current_attempt_id)
            buf = self.attempts.get(key)
            if buf is None:
                ws.active = False
                ws.current_attempt_id = None
                ws.current_source_stroke_id = None
                ws.current_start_ms = None
                ws.current_points = 0
                continue

            if buf.last_arrival_ms and (now_ms - buf.last_arrival_ms) >= self.idle_finalize_ms:
                self._finalize_locked(
                    ws.device_number,
                    wand_id,
                    ws.current_attempt_id,
                    close_reason="idle_timeout",
                )

    def finalize_idle_attempts(self):
        with self.lock:
            self._finalize_idle_attempts_locked(int(time.time() * 1000))

    def snapshot(self):
        with self.lock:
            return {
                "idle_finalize_ms": self.idle_finalize_ms,
                "attempt_buffer_sizes": {str(k): len(v.points) for k, v in self.attempts.items()},
                "last_event": None if self.last_event is None else self.last_event.__dict__,
                "last_result_keys": [f"{k[0]},{k[1]}" for k in self.last_result.keys()],
                "wands": {str(k): self.wand_status[k].__dict__ for k in self.wand_status},
            }

state = BrainState()


def _wand_status_payload(ws: WandStatus) -> dict:
    payload = ws.__dict__.copy()
    if ws.current_start_ms is not None and ws.last_point_ms is not None:
        payload["current_duration_ms"] = max(0, ws.last_point_ms - ws.current_start_ms)
    else:
        payload["current_duration_ms"] = None
    return payload


class IdleAttemptFinalizer:
    def __init__(self, state: BrainState, interval_ms: int = IDLE_SWEEP_INTERVAL_MS):
        self.state = state
        self.interval_s = interval_ms / 1000.0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self):
        while not self._stop.wait(self.interval_s):
            self.state.finalize_idle_attempts()

def on_udp_packet(raw: bytes, addr):
    ev = parse_packet(raw)
    if ev is None:
        return
    state.on_event(ev)

udp = UdpReceiver(host="0.0.0.0", port=41000, on_packet=on_udp_packet)
idle_finalizer = IdleAttemptFinalizer(state)

@app.on_event("startup")
def _startup():
    udp.start()
    idle_finalizer.start()


@app.on_event("shutdown")
def _shutdown():
    idle_finalizer.stop()
    udp.stop()

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
        "idle_finalize_ms": state.idle_finalize_ms,
    }

# 2) /api/v1/wands
@app.get("/api/v1/wands")
def api_wands():
    now_ms = int(time.time() * 1000)
    with state.lock:
        wands = [_wand_status_payload(ws) for ws in state.wand_status.values()]
    return {
        "time_ms": now_ms,
        "wands": wands,
    }

# 3) /api/v1/wand/{wand_id}
@app.get("/api/v1/wand/{wand_id}")
def api_wand(wand_id: int = Path(..., ge=1)):
    with state.lock:
        ws = state.wand_status.get(wand_id)
        payload = None if ws is None else _wand_status_payload(ws)
    if ws is None:
        raise HTTPException(status_code=404, detail="wand not found")
    return payload

def _attempt_result_payload(res: FinalResult):
    return {
        "attempt_id": res.attempt_id,
        "source_stroke_id": res.source_stroke_id,
        "wand_id": res.wand_id,
        "device_number": res.device_number,
        "start_ms": res.start_ms,
        "end_ms": res.end_ms,
        "duration_ms": max(0, res.end_ms - res.start_ms),
        "num_points": res.num_points,
        "result": {
            "status": res.status,
            "close_reason": res.close_reason,
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
    with state.lock:
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
    with state.lock:
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
    with state.lock:
        render_path = state.live_render_path.get(wand_id)
        candidates = [r for r in state.last_result.values() if r.wand_id == wand_id]
    if not render_path:
        # Fallback: serve latest finalized attempt for this wand if available.
        if not candidates:
            raise HTTPException(status_code=404, detail="no live image for this wand")
        render_path = max(candidates, key=lambda r: r.finalized_at_ms).render_path
    resp = FileResponse(render_path, media_type="image/png")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


# ----------------------------
# V2 Scoring APIs (versioned work area)
# ----------------------------

@app.get("/api/v2/templates")
def api_v2_templates():
    ts = list_templates(TEMPLATES_DIR)
    return {
        "count": len(ts),
        "templates": [
            {
                "template_id": t.template_id,
                "name": t.name,
                "image_png": f"/api/v2/template/{t.template_id}/image.png",
            }
            for t in ts
        ],
    }


@app.api_route("/api/v2/template/{template_id}/image.png", methods=["GET", "HEAD"])
def api_v2_template_image(template_id: str = Path(..., min_length=1)):
    p = TEMPLATES_DIR / f"{template_id}.png"
    if not p.exists():
        raise HTTPException(status_code=404, detail="template not found")
    return FileResponse(str(p), media_type="image/png")


def _resolve_attempt_for_scoring(wand_id: Optional[int], attempt_id: Optional[int]) -> FinalResult:
    with state.lock:
        if attempt_id is not None:
            res = state.attempt_index.get(attempt_id)
            if res is None:
                raise HTTPException(status_code=404, detail="attempt not found")
            return res

        if wand_id is None:
            raise HTTPException(status_code=400, detail="wand_id or attempt_id is required")
        candidates = [r for r in state.last_result.values() if r.wand_id == wand_id]
    if attempt_id is not None:
        raise HTTPException(status_code=500, detail="unexpected attempt resolution path")
    if not candidates:
        raise HTTPException(status_code=404, detail="no attempt yet for this wand")
    return max(candidates, key=lambda r: r.finalized_at_ms)


@app.get("/api/v2/score/latest")
def api_v2_score_latest(
    wand_id: int = Query(..., ge=1),
    template_id: Optional[str] = Query(None),
):
    res = _resolve_attempt_for_scoring(wand_id=wand_id, attempt_id=None)
    return _score_attempt_payload(res, template_id=template_id)


@app.get("/api/v2/score/attempt/{attempt_id}")
def api_v2_score_attempt(
    attempt_id: int = Path(..., ge=0),
    template_id: Optional[str] = Query(None),
):
    res = _resolve_attempt_for_scoring(wand_id=None, attempt_id=attempt_id)
    return _score_attempt_payload(res, template_id=template_id)


def _score_attempt_payload(res: FinalResult, template_id: Optional[str]):
    templates = list_templates(TEMPLATES_DIR)
    if not templates:
        raise HTTPException(
            status_code=400,
            detail="no templates found in data/templates (expected *.png)",
        )

    if template_id:
        chosen = next((t for t in templates if t.template_id == template_id), None)
        if chosen is None:
            raise HTTPException(status_code=404, detail="template not found")
        best = compute_score(FSPath(res.render_path), FSPath(chosen.path))
        candidates = [best]
    else:
        candidates = [compute_score(FSPath(res.render_path), FSPath(t.path)) for t in templates]
        best = max(candidates, key=lambda c: c.score)

    # Also write back into last result payload fields for convenience.
    res.best_template_id = best.template_id
    res.best_template_name = best.template_name
    res.score = best.score

    return {
        "attempt_id": res.attempt_id,
        "source_stroke_id": res.source_stroke_id,
        "wand_id": res.wand_id,
        "device_number": res.device_number,
        "num_points": res.num_points,
        "close_reason": res.close_reason,
        "best": {
            "template_id": best.template_id,
            "template_name": best.template_name,
            "score": best.score,
            "metrics": best.metrics,
        },
        "all_candidates": [
            {
                "template_id": c.template_id,
                "template_name": c.template_name,
                "score": c.score,
                "metrics": c.metrics,
            }
            for c in sorted(candidates, key=lambda x: x.score, reverse=True)
        ],
        "attempt_image_png": f"/api/v1/attempt/{res.attempt_id}/image.png",
    }
