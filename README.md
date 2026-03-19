# FPGA-Wand

Distributed wand-tracking, drawing, and scoring system built for Information
Processing Group 10.

## Top-Level Structure

The repo is now organized around three main implementation areas:

- [hardware/](hardware/)
  physical artefacts and subsystem notes for the wand and camera setup.
- [FPGA/](FPGA/)
  PYNQ / FPGA runtime code plus archived Vivado-style design artefacts.
- [software/](software/)
  EC2-side cloud service, protocol docs, and software-side utilities.

Supporting documentation still lives under [docs/](docs/).

## System Overview

The live system turns a bright LED wand tip into a scored drawing:

1. The camera observes the wand tip.
2. The FPGA design computes centroid-style statistics for bright pixels.
3. The PYNQ PS software filters the result and emits one UDP point packet per
   valid sample.
4. The EC2 Wand Brain service reconstructs strokes in memory, rasterizes them,
   scores them against templates, and stores finalized attempts.
5. A browser dashboard polls the cloud service for live status, control,
   attempts, timing, and leaderboards.

The architecture deliberately separates:

- UDP as the low-latency point-stream data plane
- HTTP as the control and dashboard plane

## Where To Look

### Hardware

- [hardware/README.md](hardware/README.md)
- [hardware/wand/current_led_wand/README.md](hardware/wand/current_led_wand/README.md)
- [hardware/camera/README.md](hardware/camera/README.md)

### FPGA

- [FPGA/README.md](FPGA/README.md)
- [FPGA/runtime/pynq_wand_brain_demo.py](FPGA/runtime/pynq_wand_brain_demo.py)
- [FPGA/runtime/pynq_udp_bridge.py](FPGA/runtime/pynq_udp_bridge.py)
- [FPGA/designs/README.md](FPGA/designs/README.md)

### Software

- [software/README.md](software/README.md)
- [software/cloud/main.py](software/cloud/main.py)
- [software/cloud/frontend/index.html](software/cloud/frontend/index.html)
- [software/protocol/protocol/pynq-udp-brian-v1.md](software/protocol/protocol/pynq-udp-brian-v1.md)
- [software/tools/README.md](software/tools/README.md)

## Local Development

### Cloud App

```bash
cd software/cloud
bash start_script.sh --install-deps
```

Then open:

```text
http://127.0.0.1:8000/
```

### PYNQ Sender

The board-side sender lives in:

- [FPGA/runtime/pynq_wand_brain_demo.py](FPGA/runtime/pynq_wand_brain_demo.py)

The main demo defaults to the current EC2 public IP but can also be overridden
with the `BRAIN_HOST` environment variable.

Per-board identity still matters:

- `DEVICE_NUMBER`
- `WAND_ID`

## Runtime Data

Runtime-generated files are intentionally not the source of truth for GitHub:

- `software/cloud/data/fpgawand.sqlite3`
- `software/cloud/data/node_control_state.json`
- `software/cloud/data/outputs/*.png`
- EC2 deployment-only backups such as `cloud/alt_live_console`

The authoritative template source images live in:

- [software/cloud/backend/versions/brain_v2_scoring/data/templates](software/cloud/backend/versions/brain_v2_scoring/data/templates)

## Notes For Committers

Commit the canonical source under `hardware/`, `FPGA/`, `software/`, and
`docs/`. Avoid committing runtime-only data copied back from local runs or EC2.
