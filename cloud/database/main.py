import os
import time
from fastapi import FastAPI, HTTPException, Path, Query, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from pathlib import Path as FSPath
from sqlalchemy.orm import Session

from database.database import Base, engine, SessionLocal
from database.models import Attempt

from brain.ingest.udp_rx import UdpReceiver
from brain.ingest.parser import parse_packet, PointEvent
from brain.render.rasterize import rasterize


# ----------------------------
# Setup
# ----------------------------

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FPGA-Wand Brain", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTDIR = FSPath("data/outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)

Point = Tuple[float, float, int]


# ----------------------------
# Brain State (unchanged logic)
# ----------------------------

@dataclass
class AttemptBuffer:
    points: List[Point] = field(default_factory=list)


class BrainState:
    def __init__(self):
        self.attempts: Dict[tuple[int, int, int], AttemptBuffer] = {}

    def on_event(self, ev: PointEvent):
        key = (ev.device_number, ev.wand_id, ev.stroke_id)

        if ev.pen_down:
            buf = self.attempts.setdefault(key, AttemptBuffer())
            buf.points.append((ev.x, ev.y, ev.timestamp_ms))

        if ev.stroke_end:
            self._finalize(ev.device_number, ev.wand_id, ev.stroke_id)

    def _finalize(self, device, wand, attempt_id):
        key = (device, wand, attempt_id)
        buf = self.attempts.get(key)
        if not buf:
            return

        pts = buf.points
        start_ms = pts[0][2]
        end_ms = pts[-1][2]
        finalized_at_ms = int(time.time() * 1000)

        img = rasterize(pts, size=256, stroke=3)
        out_path = OUTDIR / f"dev{device}_wand{wand}_{finalized_at_ms}.png"
        img.save(out_path)

        # 🔥 Save to database
        db = SessionLocal()
        try:
            attempt = Attempt(
                wand_id=wand,
                attempt_id=attempt_id,
                device_number=device,
                start_ms=start_ms,
                end_ms=end_ms,
                finalized_at_ms=finalized_at_ms,
                num_points=len(pts),
                render_path=str(out_path),
            )
            db.add(attempt)
            db.commit()
        finally:
            db.close()

        self.attempts.pop(key, None)


state = BrainState()


def on_udp_packet(raw: bytes, addr):
    ev = parse_packet(raw)
    if ev:
        state.on_event(ev)


udp = UdpReceiver(host="0.0.0.0", port=41000, on_packet=on_udp_packet)


@app.on_event("startup")
def startup():
    udp.start()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/database/attempts")
def api_database_attempts(db: Session = Depends(get_db)):
    attempts = db.query(Attempt).order_by(Attempt.id.desc()).limit(20).all()
    return [
        {
            "id": a.id,
            "wand_id": a.wand_id,
            "attempt_id": a.attempt_id,
            "device_number": a.device_number,
            "num_points": a.num_points,
            "score": a.score,
            "status": a.status,
            "created_at": str(a.created_at),
        }
        for a in attempts
    ]


# ----------------------------
# API Endpoints
# ----------------------------

@app.get("/api/v1/health")
def health():
    return {"ok": True}


@app.get("/api/v1/attempt/latest")
def latest_attempt(wand_id: int = Query(...)):
    db = SessionLocal()
    try:
        attempt = (
            db.query(Attempt)
            .filter(Attempt.wand_id == wand_id)
            .order_by(Attempt.finalized_at_ms.desc())
            .first()
        )
        if not attempt:
            raise HTTPException(status_code=404, detail="No attempts")

        return {
            "attempt_id": attempt.attempt_id,
            "image_png": f"/api/v1/attempt/{attempt.id}/image.png",
            "score": attempt.score,
        }
    finally:
        db.close()


@app.get("/api/v1/attempt/{attempt_db_id}/image.png")
def attempt_image(attempt_db_id: int = Path(...)):
    db = SessionLocal()
    try:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_db_id).first()
        if not attempt:
            raise HTTPException(status_code=404)

        return FileResponse(attempt.render_path, media_type="image/png")
    finally:
        db.close()


# ----------------------------
# Frontend
# ----------------------------

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")