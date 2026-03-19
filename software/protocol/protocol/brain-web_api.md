# Wand Brain HTTP API Overview

This document summarizes the current HTTP-facing interfaces exposed by the cloud
service.

## API Families

### `/api/v1/*` Live Runtime

Core live-status and rendered-image APIs:

- `GET /api/v1/health`
- `GET /api/v1/wands`
- `GET /api/v1/wand/{wand_id}`
- `GET /api/v1/wand/{wand_id}/live.png`
- `GET /api/v1/attempt/latest?wand_id=<id>`
- `GET /api/v1/attempt/{attempt_id}/image.png`
- `GET /api/v1/database/health`
- `GET /api/v1/database/attempts`

### `/api/v2/*` Templates And Scoring

- `GET /api/v2/templates`
- `GET /api/v2/template/{template_id}/image.png`
- `GET /api/v2/wand/{wand_id}/target-template`
- `PUT /api/v2/wand/{wand_id}/target-template?template_id=...`
- `GET /api/v2/score/latest?wand_id=<id>&template_id=<optional>`
- `GET /api/v2/score/attempt/{attempt_id}?template_id=<optional>`

### `/api/v3/*` Node Control And Leaderboards

- `GET /api/v3/node-controls`
- `GET /api/v3/node/{device_number}/control`
- `PUT /api/v3/node/{device_number}/control`
- `GET /api/v3/node/{device_number}/status`
- `POST /api/v3/node/{device_number}/ack`
- `GET /api/v3/leaderboards`
- `POST /api/v3/leaderboards/claim`

## Architectural Notes

- The website is a polling dashboard over HTTP.
- UDP is used only for live point ingestion.
- The frontend does not talk to the UDP receiver directly.
- Live attempt state is held in memory.
- Finalized attempts, scores, and champions are persisted.

## Important Semantics

- Public `attempt_id` is the backend's internal finalized-attempt identifier.
- UDP `stroke_id` is treated as a source-side stroke identifier and is surfaced
  separately as `source_stroke_id` where relevant.
- Node control is a separate HTTP control plane from the UDP data path.
