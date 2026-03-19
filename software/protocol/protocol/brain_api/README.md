# Wand Brain API Guides

These guides document the HTTP-facing Brain features by functional area rather
than as one flat endpoint list.

## Entry Points

- [Live Runtime And Plotting](./live_runtime_and_plotting.md)
  live wand state, live PNG rendering, finalized attempts, and the polling
  dashboard flow.
- [Templates, Scoring, And Target Selection](./templates_scoring_and_target_selection.md)
  template discovery, per-wand target template selection, and scoring APIs.
- [Node Control](./node_control.md)
  the HTTP control plane used to influence PYNQ runtime behavior.
- [Leaderboards And Persistence](./leaderboards_and_persistence.md)
  finalized-attempt persistence, database inspection, and champion claiming.

## Main Implementation Files

- app composition:
  [`../../../cloud/main.py`](../../../cloud/main.py)
- core live runtime:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- UDP ingress:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py)
- packet parser:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py)
- renderer:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/render/rasterize.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/render/rasterize.py)
- scoring:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py)
- node-control store:
  [`../../../cloud/node_control.py`](../../../cloud/node_control.py)
- persistence models:
  [`../../../cloud/database/models.py`](../../../cloud/database/models.py)

## Architectural Summary

The Brain service is composed in two layers:

1. the base live runtime in `brain_v2_scoring`
2. the repo-level wrapper in `software/cloud/main.py`

The base runtime owns:

- UDP ingestion
- point parsing
- in-memory attempt buffering
- live and finalized image rendering
- template scoring primitives
- core `/api/v1/*` and `/api/v2/*` routes

The wrapper adds:

- static frontend serving
- template-selection state per wand
- persistent database storage for finalized attempts
- node-control APIs
- leaderboard APIs

That split is important when reading the code: some endpoints are implemented in
`server.py`, while others are layered on top in `main.py`.
