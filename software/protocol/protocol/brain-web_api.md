# Wand Brain HTTP API Overview

This document is the top-level index for the Brain service's HTTP APIs.

The service is composed from:

- the base live runtime in
  [`../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- the wrapper layer in
  [`../../cloud/main.py`](../../cloud/main.py)

The base runtime owns live ingest and rendering. The wrapper adds persistence,
template selection, node control, leaderboards, and the frontend shell.

## Served UI Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | serve the main dashboard page |
| `GET` | `/frontend/*` | serve frontend static assets |

These are composed in [`software/cloud/main.py`](../../cloud/main.py).

## API Families

### `/api/v1/*` Live Runtime And History

Detailed guide:
[brain_api/live_runtime_and_plotting.md](./brain_api/live_runtime_and_plotting.md)

Main routes:

- `GET /api/v1/health`
- `GET /api/v1/wands`
- `GET /api/v1/wand/{wand_id}`
- `GET /api/v1/wand/{wand_id}/live.png`
- `GET /api/v1/attempt/latest?wand_id=<id>`
- `GET /api/v1/attempt/{attempt_id}/image.png`
- `GET /api/v1/database/health`
- `GET /api/v1/database/attempts`

### `/api/v2/*` Templates, Target Selection, And Scoring

Detailed guide:
[brain_api/templates_scoring_and_target_selection.md](./brain_api/templates_scoring_and_target_selection.md)

Main routes:

- `GET /api/v2/templates`
- `GET /api/v2/template/{template_id}/image.png`
- `GET /api/v2/wand/{wand_id}/target-template`
- `PUT /api/v2/wand/{wand_id}/target-template?template_id=...`
- `GET /api/v2/score/latest?wand_id=<id>&template_id=<optional>`
- `GET /api/v2/score/attempt/{attempt_id}?template_id=<optional>`

### `/api/v3/*` Node Control, Leaderboards, And Persistence Views

Detailed guides:

- [brain_api/node_control.md](./brain_api/node_control.md)
- [brain_api/leaderboards_and_persistence.md](./brain_api/leaderboards_and_persistence.md)

Main routes:

- `GET /api/v3/node-controls`
- `GET /api/v3/node/{device_number}/control`
- `PUT /api/v3/node/{device_number}/control`
- `GET /api/v3/node/{device_number}/status`
- `POST /api/v3/node/{device_number}/ack`
- `GET /api/v3/leaderboards`
- `POST /api/v3/leaderboards/claim`

## Cross-Cutting Architectural Notes

- The website is a polling dashboard over HTTP, not a WebSocket application.
- UDP is reserved for live point ingestion only.
- The frontend never talks directly to the UDP receiver.
- Live attempt state is held in memory inside the runtime.
- Finalized attempts, scores, and champions are persisted by the wrapper layer.

## Important Semantics

- Public `attempt_id` is the backend-owned finalized-attempt identifier.
- UDP `stroke_id` is treated as source metadata and is exposed separately as
  `source_stroke_id`.
- Node control is a separate HTTP control plane from the UDP data path.
- Finalized-attempt history and leaderboard data are layered on top of the
  lower-level live runtime.
