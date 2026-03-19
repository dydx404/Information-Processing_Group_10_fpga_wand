# FPGA-Wand

Distributed FPGA-to-cloud wand tracking, drawing, and scoring system built for
Information Processing Group 10.

## What The System Does

The live system turns a bright wand tip into a scored drawing:

1. A PYNQ board captures frames from a camera.
2. The FPGA design computes centroid statistics for bright pixels.
3. The PYNQ PS software filters those results and emits one UDP packet per valid
   point.
4. The EC2 Wand Brain service reconstructs each stroke in memory, rasterizes it
   into a drawing, scores it against a selected template, and stores finalized
   attempts in a database.
5. A browser-based live console polls the service for live status, controls,
   recent attempts, and leaderboards.

The system deliberately separates the fast data path from the flexible control
path:

- UDP is the low-latency point-stream data plane.
- HTTP is the control and dashboard plane.

## Current Architecture

### 1. PYNQ Node

The node-side logic lives primarily under [wand/](wand/).

- PL accelerates centroid-style pixel reduction.
- PS handles camera capture, preprocessing, DMA, MMIO reads, validity checks,
  local sketching, and networking.
- The PS sender packages points using the `wb-point-v1` binary UDP protocol and
  also polls HTTP node-control endpoints from the server.

Key files:

- [wand/fpga/pynq_wand_brain_demo.py](wand/fpga/pynq_wand_brain_demo.py)
- [wand/fpga/pynq_udp_bridge.py](wand/fpga/pynq_udp_bridge.py)

### 2. Wand Brain Cloud Service

The canonical cloud source lives under [cloud/](cloud/).

- `cloud/main.py` is the repo-level FastAPI entrypoint and glue layer.
- `cloud/backend/versions/brain_v2_scoring/src/brain/` contains the live
  runtime for UDP ingest, rendering, and scoring.
- `cloud/database/` contains SQLAlchemy models and DB configuration.
- `cloud/frontend/index.html` is the live console UI.
- `cloud/node_control.py` stores revisioned control and ack state for each node.

Important design choices:

- Live stroke state stays in memory.
- Finalized attempts are persisted.
- Scoring happens on finalized attempts, not every frame.
- The frontend uses HTTP polling rather than WebSockets.

### 3. EC2 Deployment Shape

On EC2, the app is deployed from a runtime copy under `cloud/alt_live_console`.
That directory is deployment state, not the canonical source tree to edit for
GitHub.

The canonical source to commit is the repo version under [cloud/](cloud/).

## Repository Layout

```text
cloud/       Wand Brain backend, database layer, frontend, start script
docs/        Project notes and integration docs
protocol/    Protocol specifications, including wb-point-v1 UDP
tools/       Test and observable demo utilities
wand/        PYNQ / FPGA-side code and helpers
```

Helpful directory indexes:

- [cloud/README.md](cloud/README.md)
- [docs/README.md](docs/README.md)
- [tools/README.md](tools/README.md)
- [wand/README.md](wand/README.md)

## Local Development

### Cloud App

From the repo root:

```bash
cd cloud
bash start_script.sh --install-deps
```

Then open:

```text
http://127.0.0.1:8000/
```

### PYNQ Sender

The main demo defaults to the current EC2 public IP but can also be overridden
with the `BRAIN_HOST` environment variable in
[wand/fpga/pynq_wand_brain_demo.py](wand/fpga/pynq_wand_brain_demo.py).

Per-board identity still matters:

- `DEVICE_NUMBER`
- `WAND_ID`

## Data And Runtime Files

Runtime-generated files are intentionally not the source of truth for GitHub:

- `cloud/data/fpgawand.sqlite3`
- `cloud/data/node_control_state.json`
- `cloud/data/outputs/*.png`
- EC2 deployment-only backups under `cloud/alt_live_console`

The authoritative templates live in:

- [cloud/backend/versions/brain_v2_scoring/data/templates](cloud/backend/versions/brain_v2_scoring/data/templates)

## Protocol Reference

The point-stream protocol is documented here:

- [protocol/protocol/pynq-udp-brian-v1.md](protocol/protocol/pynq-udp-brian-v1.md)

## Current Features

- Live UDP point ingest on port `41000`
- HTTP API and dashboard on port `8000`
- Template selection and scoring
- Per-template leaderboards and champion naming
- HTTP node control with ack tracking
- Stroke timing
- Multi-wand support

## Notes For Committers

When preparing GitHub commits, prefer the canonical repo files and avoid
committing runtime-only data or EC2 deployment artifacts.
