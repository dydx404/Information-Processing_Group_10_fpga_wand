# Cloud Service

This directory contains the canonical cloud-side source for the current Wand
Brain deployment.

## Main Pieces

- [main.py](main.py)
  repo-level FastAPI entrypoint that wraps the live runtime with persistence,
  leaderboards, node control, and the frontend.
- [start_script.sh](start_script.sh)
  preferred launcher for the current cloud app.
- [frontend/](frontend/)
  single-page polling dashboard served by the same FastAPI process.
- [database/](database/)
  SQLAlchemy configuration and persisted models.
- [backend/](backend/)
  live UDP ingest, rendering, and scoring runtime packages.
- [data/](data/)
  local runtime files such as the SQLite database, node-control state, and
  generated output images.

## Canonical vs Runtime

Edit the source in this directory tree for GitHub.

Do not treat EC2 deployment copies such as `cloud/alt_live_console` as the
long-term source of truth. Those are runtime artifacts of deployment.

## Start Here

For most contributors, the most useful files are:

- [main.py](main.py)
- [frontend/index.html](frontend/index.html)
- [database/models.py](database/models.py)
- [backend/versions/brain_v2_scoring/src/brain/api/server.py](backend/versions/brain_v2_scoring/src/brain/api/server.py)

## API Documentation

The detailed API guides live under the protocol docs:

- [../protocol/protocol/brain-web_api.md](../protocol/protocol/brain-web_api.md)
- [../protocol/protocol/brain_api/README.md](../protocol/protocol/brain_api/README.md)

Those documents explain the served Brain features by API family, including:

- live plotting and attempt images
- templates and scoring
- node control
- leaderboards and persistence

## Architecture Reports

More formal backend reports live under:

- [report/README.md](report/README.md)
- [report/backend_system_report.md](report/backend_system_report.md)
- [report/webpage_architecture_report.md](report/webpage_architecture_report.md)
- [report/database_architecture_report.md](report/database_architecture_report.md)
