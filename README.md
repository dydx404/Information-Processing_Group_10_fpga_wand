# FPGA-Wand

FPGA-Wand is a distributed drawing system: a bright LED wand is tracked by a
camera, reduced to centroid data on a PYNQ-Z1, streamed to a cloud service,
and turned into live drawings, scores, leaderboards, and node-control actions.

## Start Here

If you are new to the repo, read these in order:

1. [docs/newcomer_guide.md](docs/newcomer_guide.md)
2. [docs/architecture/overview.md](docs/architecture/overview.md)
3. [FPGA/README.md](FPGA/README.md)
4. [software/README.md](software/README.md)

If you want a quick system explanation first, the project flow is:

```mermaid
flowchart LR
    W[LED Wand Tip] --> C[Camera]
    C --> PS[PYNQ PS Runtime]
    PS --> DMA[AXI DMA]
    DMA --> PL[Centroid PL IP]
    PL --> PS
    PS --> UDP[UDP Point Stream]
    UDP --> WB[Wand Brain on EC2]
    WB --> DB[(SQLite / Persistence)]
    WB --> UI[Live Web Console]
    UI --> HTTP[HTTP Control]
    HTTP --> PS
```

## Repo Map

The repository is organized around the three main implementation areas plus a
shared documentation tree:

- [hardware/](hardware/)
  physical build information for the wand and camera setup
- [FPGA/](FPGA/)
  the adopted PYNQ runtime plus FPGA design artefacts
- [software/](software/)
  the cloud service, protocol definitions, and software-side tools
- [docs/](docs/)
  architecture, validation, report material, and group/project-management notes

## Choose A Path

| If you want to understand... | Open this first | Then go here |
| --- | --- | --- |
| The whole system in 10 minutes | [docs/newcomer_guide.md](docs/newcomer_guide.md) | [docs/architecture/overview.md](docs/architecture/overview.md) |
| The FPGA and PYNQ path | [FPGA/README.md](FPGA/README.md) | [FPGA/runtime/ps_pl_flow.md](FPGA/runtime/ps_pl_flow.md) |
| The UDP protocol and point flow | [software/protocol/README.md](software/protocol/README.md) | [software/protocol/protocol/pynq-udp-flow.md](software/protocol/protocol/pynq-udp-flow.md) |
| The Wand Brain backend | [software/cloud/README.md](software/cloud/README.md) | [software/cloud/report/backend_system_report.md](software/cloud/report/backend_system_report.md) |
| The frontend and live console | [software/cloud/frontend/README.md](software/cloud/frontend/README.md) | [software/cloud/frontend/index.html](software/cloud/frontend/index.html) |
| The database model and persistence | [software/cloud/database/README.md](software/cloud/database/README.md) | [software/cloud/database/models.py](software/cloud/database/models.py) |
| Validation evidence | [docs/testing/system_validation_report.md](docs/testing/system_validation_report.md) | [software/tools/README.md](software/tools/README.md) |

## What The Final System Does

The final presented system follows this path:

1. A camera observes a bright LED wand tip.
2. The PYNQ PS preprocesses the frame into a binary image.
3. AXI DMA streams the image into a custom centroid IP in the PL.
4. The PS reads centroid statistics, filters them, and maintains stroke logic.
5. The PS sends accepted points to Wand Brain over UDP.
6. Wand Brain reconstructs attempts, renders images, scores them, stores
   finalized results, and serves the live dashboard.
7. The dashboard can also send HTTP control messages back to the PYNQ node.

The architecture deliberately separates:

- UDP as the low-latency point-stream data plane
- HTTP as the control and dashboard plane

## Local Development

### Run the cloud app

```bash
cd software/cloud
bash start_script.sh --install-deps
```

Then open:

```text
http://127.0.0.1:8000/
```

### Run the PYNQ sender

The board-side demo is:

- [FPGA/runtime/pynq_wand_brain_demo.py](FPGA/runtime/pynq_wand_brain_demo.py)

The main demo can use the configured EC2 address or an overridden
`BRAIN_HOST` value. Each board also needs its own:

- `DEVICE_NUMBER`
- `WAND_ID`

## Source Of Truth

This repo contains both **canonical source** and **runtime-generated data**.
For newcomers, the key distinction is:

- edit and read the source under `hardware/`, `FPGA/`, `software/`, and `docs/`
- do not treat runtime-generated files as the authoritative implementation

Runtime-generated files are intentionally not the source of truth for GitHub:

- `software/cloud/data/fpgawand.sqlite3`
- `software/cloud/data/node_control_state.json`
- `software/cloud/data/outputs/*.png`
- EC2 deployment-only copies such as `cloud/alt_live_console`

The authoritative template source images live in:

- [software/cloud/backend/versions/brain_v2_scoring/data/templates](software/cloud/backend/versions/brain_v2_scoring/data/templates)

## Notes For Contributors

Commit the canonical source under `hardware/`, `FPGA/`, `software/`, and
`docs/`. Avoid committing runtime-only data copied back from local runs or EC2.
