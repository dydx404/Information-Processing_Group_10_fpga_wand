from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from brain.ingest.udp_rx import UdpReceiver
from brain.ingest.parser import parse_packet
from brain.core.state import BrainState
from brain.render.rasterize import rasterize

app = FastAPI(title="FPGA-Wand Brain")

state = BrainState()

OUTDIR = Path("data/outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)

def on_udp_packet(raw: bytes, addr):
    ev = parse_packet(raw)
    if ev is not None:
        state.add_event(ev)

udp = UdpReceiver(host="0.0.0.0", port=9999, on_packet=on_udp_packet)

@app.on_event("startup")
def _startup():
    udp.start()

@app.get("/")
def root():
    return {"service": "fpga-wand-brain"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/debug/latest-packet")
def latest_packet():
    raw = udp.latest.raw
    return {"from": udp.latest.addr, "len": len(raw), "hex": raw.hex()}

@app.get("/v1/debug/state")
def debug_state():
    return state.snapshot()

@app.get("/v1/render/latest")
def render_latest(wand_id: int = 1):
    pts = state.buffers.get(wand_id, [])
    if not pts:
        raise HTTPException(status_code=404, detail="No points for this wand_id")

    img = rasterize(pts, size=256, stroke=3)
    out_path = OUTDIR / f"wand_{wand_id}_latest.png"
    img.save(out_path)
    state.last_render_path[wand_id] = str(out_path)
    return {"wand_id": wand_id, "points": len(pts), "path": str(out_path)}

from fastapi.responses import FileResponse

@app.get("/v1/render/latest.png")
def render_latest_png(wand_id: int = 1):
    _ = render_latest(wand_id=wand_id)
    path = state.last_render_path.get(wand_id)

    resp = FileResponse(path, media_type="image/png")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp
