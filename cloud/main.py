from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from fastapi import Body, HTTPException, Path as ApiPath, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

CLOUD_DIR = Path(__file__).resolve().parent
BRAIN_APP_DIR = CLOUD_DIR / "backend" / "versions" / "brain_v2_scoring"
BRAIN_SRC_DIR = BRAIN_APP_DIR / "src"
DEFAULT_TEMPLATE_DIR = BRAIN_APP_DIR / "data" / "templates"
CLOUD_DATA_DIR = CLOUD_DIR / "data"
CLOUD_TEMPLATE_DIR = CLOUD_DATA_DIR / "templates"
CLOUD_OUTPUT_DIR = CLOUD_DATA_DIR / "outputs"
FRONTEND_DIR = CLOUD_DIR / "frontend"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wand-brain-cloud")


def ensure_runtime_assets() -> None:
    CLOUD_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    CLOUD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

    for src in sorted(DEFAULT_TEMPLATE_DIR.glob("*.png")):
        dst = CLOUD_TEMPLATE_DIR / src.name
        if not dst.exists():
            shutil.copy2(src, dst)


ensure_runtime_assets()
os.chdir(CLOUD_DIR)

if str(BRAIN_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_SRC_DIR))

from database.database import Base, SessionLocal, engine  # noqa: E402
from database.models import Attempt, TemplateChampion  # noqa: E402
from node_control import NodeControlStore  # noqa: E402
import brain.api.server as brain_server  # noqa: E402
from brain.api.server import FinalResult, app, state  # noqa: E402
from brain.scoring import compute_score, list_templates  # noqa: E402

DB_READY = False
_DB_WARNING: str | None = None
selected_template_by_wand: dict[int, str] = {}
attempt_template_by_key: dict[tuple[int, int, int], str] = {}
node_control_store = NodeControlStore(CLOUD_DATA_DIR / "node_control_state.json")
CHAMPION_SCORE_EPSILON = 1e-9


def initialize_database() -> None:
    global DB_READY, _DB_WARNING
    if DB_READY:
        return
    try:
        Base.metadata.create_all(bind=engine)
        DB_READY = True
        _DB_WARNING = None
        logger.info("Database ready")
    except Exception as exc:  # pragma: no cover - startup fallback path
        DB_READY = False
        _DB_WARNING = str(exc)
        logger.warning("Database unavailable: %s", exc)


def backfill_template_champions() -> int:
    initialize_database()
    if not DB_READY:
        return 0

    with SessionLocal() as db:
        attempts = (
            db.query(Attempt)
            .filter(Attempt.best_template_id.isnot(None), Attempt.score.isnot(None))
            .order_by(Attempt.finalized_at_ms.asc(), Attempt.id.asc())
            .all()
        )

        updated_templates: set[str] = set()
        for row in attempts:
            current = db.query(TemplateChampion).filter(TemplateChampion.template_id == row.best_template_id).one_or_none()
            current_attempt_id = None if current is None else current.attempt_id
            champion = _maybe_promote_template_champion(db, row)
            if champion is not None:
                db.flush()
            if champion is not None and champion.attempt_id != current_attempt_id:
                updated_templates.add(champion.template_id)

        if updated_templates:
            db.commit()
        else:
            db.rollback()
        return len(updated_templates)


@app.on_event("startup")
def _cloud_startup() -> None:
    initialize_database()
    if DB_READY:
        try:
            updated = backfill_template_champions()
            if updated:
                logger.info("Template champion backfill updated %s templates", updated)
        except Exception as exc:  # pragma: no cover - keep startup resilient
            logger.warning("Template champion backfill failed: %s", exc)


@app.get("/")
def frontend_index() -> FileResponse:
    resp = FileResponse(FRONTEND_DIR / "index.html")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


def _db_row_payload(row: Attempt) -> dict[str, Any]:
    return {
        "id": row.id,
        "attempt_id": row.attempt_id,
        "wand_id": row.wand_id,
        "device_number": row.device_number,
        "start_ms": row.start_ms,
        "end_ms": row.end_ms,
        "duration_ms": max(0, row.end_ms - row.start_ms),
        "finalized_at_ms": row.finalized_at_ms,
        "num_points": row.num_points,
        "status": row.status,
        "best_template_id": row.best_template_id,
        "best_template_name": row.best_template_name,
        "score": row.score,
        "render_path": row.render_path,
        "image_png": f"/api/v1/attempt/{row.attempt_id}/image.png",
        "created_at": None if row.created_at is None else row.created_at.isoformat(),
    }


def _champion_payload(row: TemplateChampion) -> dict[str, Any]:
    return {
        "id": row.id,
        "template_id": row.template_id,
        "template_name": row.template_name,
        "attempt_id": row.attempt_id,
        "wand_id": row.wand_id,
        "device_number": row.device_number,
        "finalized_at_ms": row.finalized_at_ms,
        "score": row.score,
        "player_name": row.player_name,
        "claimed": bool(row.player_name),
        "image_png": f"/api/v1/attempt/{row.attempt_id}/image.png",
        "claimed_at": None if row.claimed_at is None else row.claimed_at.isoformat(),
        "created_at": None if row.created_at is None else row.created_at.isoformat(),
        "updated_at": None if row.updated_at is None else row.updated_at.isoformat(),
    }


def _normalize_player_name(value: Any) -> str:
    cleaned = " ".join(str(value or "").split()).strip()
    if not cleaned:
        raise ValueError("player_name is required")
    if len(cleaned) > 32:
        raise ValueError("player_name must be 32 characters or fewer")
    return cleaned


def _template_refs() -> dict[str, Any]:
    return {template.template_id: template for template in list_templates(brain_server.TEMPLATES_DIR)}


def _default_template_id() -> str | None:
    refs = _template_refs()
    return next(iter(refs), None)


def _template_payload(wand_id: int, template_id: str, applies_to: str) -> dict[str, Any]:
    refs = _template_refs()
    template = refs.get(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="template not found")
    return {
        "wand_id": wand_id,
        "template_id": template.template_id,
        "template_name": template.name,
        "image_png": f"/api/v2/template/{template.template_id}/image.png",
        "applies_to": applies_to,
    }


def _json_no_store(payload: dict[str, Any]) -> JSONResponse:
    resp = JSONResponse(payload)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


def _node_payload(device_number: int) -> dict[str, Any]:
    payload = node_control_store.get_node_payload(device_number)
    return {
        "ok": True,
        "device_number": device_number,
        "control": payload["control"],
        "ack": payload["ack"],
    }


def _maybe_promote_template_champion(db, row: Attempt) -> TemplateChampion | None:
    if not row.best_template_id or row.score is None:
        return None

    champion = db.query(TemplateChampion).filter(TemplateChampion.template_id == row.best_template_id).one_or_none()

    if champion is not None and champion.attempt_id == row.attempt_id:
        champion.template_name = row.best_template_name or row.best_template_id
        champion.wand_id = row.wand_id
        champion.device_number = row.device_number
        champion.finalized_at_ms = row.finalized_at_ms
        champion.score = row.score
        db.add(champion)
        return champion

    if champion is not None and row.score <= (champion.score + CHAMPION_SCORE_EPSILON):
        return champion

    if champion is None:
        champion = TemplateChampion(template_id=row.best_template_id)

    champion.template_name = row.best_template_name or row.best_template_id
    champion.attempt_id = row.attempt_id
    champion.wand_id = row.wand_id
    champion.device_number = row.device_number
    champion.finalized_at_ms = row.finalized_at_ms
    champion.score = row.score
    champion.player_name = None
    champion.claimed_at = None
    db.add(champion)
    return champion


def upsert_attempt_record(res: FinalResult, *, promote_champion: bool = False) -> Attempt | None:
    initialize_database()
    if not DB_READY:
        return None

    with SessionLocal() as db:
        row = (
            db.query(Attempt)
            .filter(
                Attempt.device_number == res.device_number,
                Attempt.wand_id == res.wand_id,
                Attempt.attempt_id == res.attempt_id,
            )
            .one_or_none()
        )
        if row is None:
            row = Attempt(
                wand_id=res.wand_id,
                attempt_id=res.attempt_id,
                device_number=res.device_number,
                start_ms=res.start_ms,
                end_ms=res.end_ms,
                finalized_at_ms=res.finalized_at_ms,
                num_points=res.num_points,
                render_path=str(Path(res.render_path).resolve()),
                status=res.status,
                best_template_id=res.best_template_id,
                best_template_name=res.best_template_name,
                score=res.score,
            )
        else:
            row.start_ms = res.start_ms
            row.end_ms = res.end_ms
            row.finalized_at_ms = res.finalized_at_ms
            row.num_points = res.num_points
            row.render_path = str(Path(res.render_path).resolve())
            row.status = res.status
            row.best_template_id = res.best_template_id
            row.best_template_name = res.best_template_name
            row.score = res.score

        db.add(row)
        if promote_champion:
            _maybe_promote_template_champion(db, row)
        db.commit()
        db.refresh(row)
        return row


_original_finalize_locked = state._finalize_locked
_original_add_point_locked = state._add_point_locked


def _tracking_add_point_locked(ev, attempt_id: int, arrival_ms: int):
    _original_add_point_locked(ev, attempt_id=attempt_id, arrival_ms=arrival_ms)
    key = (ev.device_number, ev.wand_id, attempt_id)
    if key not in attempt_template_by_key:
        chosen = selected_template_by_wand.get(ev.wand_id) or _default_template_id()
        if chosen is not None:
            attempt_template_by_key[key] = chosen


state._add_point_locked = _tracking_add_point_locked  # type: ignore[assignment]


def _persisting_finalize_locked(device: int, wand: int, attempt_id: int, close_reason: str):
    res = _original_finalize_locked(device, wand, attempt_id, close_reason)
    if res is not None:
        key = (device, wand, attempt_id)
        template_id = attempt_template_by_key.pop(key, None)
        if template_id:
            template_path = brain_server.TEMPLATES_DIR / f"{template_id}.png"
            if template_path.exists():
                score_result = compute_score(Path(res.render_path), template_path)
                res.best_template_id = score_result.template_id
                res.best_template_name = score_result.template_name
                res.score = score_result.score
        try:
            upsert_attempt_record(res, promote_champion=True)
        except Exception as exc:  # pragma: no cover - keep live path resilient
            logger.warning("Failed to persist attempt %s/%s/%s: %s", device, wand, attempt_id, exc)
    return res


state._finalize_locked = _persisting_finalize_locked  # type: ignore[assignment]

_original_score_attempt_payload = brain_server._score_attempt_payload


def _persisting_score_attempt_payload(res: FinalResult, template_id: str | None):
    payload = _original_score_attempt_payload(res, template_id)
    try:
        upsert_attempt_record(res, promote_champion=False)
    except Exception as exc:  # pragma: no cover - keep scoring endpoint alive
        logger.warning("Failed to persist scored attempt %s: %s", res.attempt_id, exc)
    return payload


brain_server._score_attempt_payload = _persisting_score_attempt_payload


@app.get("/api/v2/wand/{wand_id}/target-template")
def api_wand_target_template(wand_id: int = ApiPath(..., ge=1)) -> dict[str, Any]:
    template_id = selected_template_by_wand.get(wand_id) or _default_template_id()
    if template_id is None:
        raise HTTPException(status_code=400, detail="no templates available")
    if wand_id not in selected_template_by_wand:
        selected_template_by_wand[wand_id] = template_id
    return _json_no_store(_template_payload(wand_id, template_id, applies_to="next_attempt"))


@app.put("/api/v2/wand/{wand_id}/target-template")
def api_set_wand_target_template(
    wand_id: int = ApiPath(..., ge=1),
    template_id: str = Query(..., min_length=1),
) -> JSONResponse:
    refs = _template_refs()
    if template_id not in refs:
        raise HTTPException(status_code=404, detail="template not found")

    selected_template_by_wand[wand_id] = template_id
    active_attempt_key = None
    with state.lock:
        ws = state.wand_status.get(wand_id)
        if ws and ws.active and ws.current_attempt_id is not None and ws.device_number is not None:
            active_attempt_key = (ws.device_number, wand_id, ws.current_attempt_id)

    applies_to = "next_attempt"
    if active_attempt_key is not None and active_attempt_key not in attempt_template_by_key:
        attempt_template_by_key[active_attempt_key] = template_id
        applies_to = "current_attempt"

    return _json_no_store(_template_payload(wand_id, template_id, applies_to=applies_to))


@app.get("/api/v3/node-controls")
def api_list_node_controls() -> JSONResponse:
    nodes = node_control_store.list_nodes()
    return _json_no_store(
        {
            "ok": True,
            "count": len(nodes),
            "nodes": nodes,
        }
    )


@app.get("/api/v3/node/{device_number}/control")
def api_get_node_control(device_number: int = ApiPath(..., ge=1)) -> JSONResponse:
    return _json_no_store(_node_payload(device_number))


@app.put("/api/v3/node/{device_number}/control")
def api_put_node_control(
    device_number: int = ApiPath(..., ge=1),
    payload: dict[str, Any] | None = Body(default=None),
) -> JSONResponse:
    try:
        node_control_store.update_control(device_number, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _json_no_store(_node_payload(device_number))


@app.get("/api/v3/node/{device_number}/status")
def api_get_node_status(device_number: int = ApiPath(..., ge=1)) -> JSONResponse:
    return _json_no_store(_node_payload(device_number))


@app.post("/api/v3/node/{device_number}/ack")
def api_post_node_ack(
    device_number: int = ApiPath(..., ge=1),
    payload: dict[str, Any] | None = Body(default=None),
) -> JSONResponse:
    try:
        ack = node_control_store.update_ack(device_number, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _json_no_store(
        {
            "ok": True,
            "device_number": device_number,
            "ack": ack,
            "control": node_control_store.get_control(device_number),
        }
    )


@app.get("/api/v3/leaderboards")
def api_v3_leaderboards() -> dict[str, Any]:
    initialize_database()
    if not DB_READY:
        raise HTTPException(status_code=503, detail=_DB_WARNING or "database unavailable")

    templates = list_templates(brain_server.TEMPLATES_DIR)
    with SessionLocal() as db:
        champions = db.query(TemplateChampion).all()

    champion_by_template = {row.template_id: row for row in champions}
    leaderboards = [
        {
            "template_id": template.template_id,
            "template_name": template.name,
            "champion": None if champion_by_template.get(template.template_id) is None else _champion_payload(champion_by_template[template.template_id]),
        }
        for template in templates
    ]
    return {
        "count": len(leaderboards),
        "leaderboards": leaderboards,
    }


@app.post("/api/v3/leaderboards/claim")
def api_v3_leaderboards_claim(payload: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
    initialize_database()
    if not DB_READY:
        raise HTTPException(status_code=503, detail=_DB_WARNING or "database unavailable")

    payload = payload or {}
    try:
        attempt_id = int(payload.get("attempt_id") or 0)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="attempt_id must be a positive integer") from exc

    if attempt_id <= 0:
        raise HTTPException(status_code=400, detail="attempt_id must be a positive integer")

    try:
        player_name = _normalize_player_name(payload.get("player_name"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with SessionLocal() as db:
        champion = db.query(TemplateChampion).filter(TemplateChampion.attempt_id == attempt_id).one_or_none()
        if champion is None:
            raise HTTPException(status_code=404, detail="attempt is not the current template champion")

        champion.player_name = player_name
        champion.claimed_at = datetime.now(timezone.utc)
        db.add(champion)
        db.commit()
        db.refresh(champion)
        return {
            "ok": True,
            "champion": _champion_payload(champion),
        }


@app.get("/api/v1/database/health")
def api_database_health() -> dict[str, Any]:
    initialize_database()
    return {
        "ok": DB_READY,
        "warning": _DB_WARNING,
    }


@app.get("/api/v1/database/attempts")
def api_database_attempts(limit: int = Query(20, ge=1, le=200)) -> dict[str, Any]:
    initialize_database()
    if not DB_READY:
        raise HTTPException(status_code=503, detail=_DB_WARNING or "database unavailable")

    with SessionLocal() as db:
        rows = (
            db.query(Attempt)
            .order_by(Attempt.finalized_at_ms.desc(), Attempt.id.desc())
            .limit(limit)
            .all()
        )

    return {
        "count": len(rows),
        "attempts": [_db_row_payload(row) for row in rows],
    }
