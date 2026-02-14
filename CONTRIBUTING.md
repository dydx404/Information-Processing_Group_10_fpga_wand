# Contributing Guide

This repository contains the group coursework project for
**Information Processing – Group 10**.

The system spans multiple layers:
- ESP32 firmware (wand)
- FPGA / Vivado hardware and drivers
- Node-side software
- Cloud backend and database

To keep the project stable, assessable, and reproducible, all
contributions must follow the rules below.

---

## 1. Branching Model (Required)

We use a **feature-branch workflow**.

### Protected branch
- `main`
  - Always demo-ready
  - No direct pushes
  - All merges must go through Pull Requests

### Working branches
Create branches from `main` using:
feature/<layer>-<short-description>

Examples:
- `feature/esp32-imu-driver`
- `feature/fpga-dma-filter`
- `feature/backend-websocket`
- `feature/protocol-v1`
---

## 2. Repository Structure and Ownership

Please place files only in their intended locations.

### Wand / Edge Node
- `wand/esp32/`  
  ESP32 firmware (PlatformIO / Arduino / ESP-IDF)

- `wand/fpga/`  
  FPGA-related work:
  - `vivado/` → TCL scripts, IP sources, constraints
  - `overlays/` → final `.bit` / `.hwh` files only
  - `drivers/` → Python or C drivers
  - `node_software/` → PYNQ / node-side software

### Cloud
- `cloud/backend/` → API and session logic
- `cloud/database/` → schema and migrations
- `cloud/infra/` → deployment scripts (e.g. EC2)

### Shared
- `protocol/` → message schemas and examples
- `docs/` → architecture, testing, report assets

If you are unsure where something belongs, ask before committing.

---

## 3. Forbidden Content

The following must **never** be committed:

- Lab code from previous coursework
- Vivado build output directories (`*.runs/`, `.cache/`, `.hw/`, etc.)
- Secrets or credentials:
  - `.pem`, `.key`, `.env`
  - API keys, tokens, passwords
- Large binary datasets
- Personal scratch files outside `tools/`

---

## 4. FPGA / Vivado Rules

- Prefer TCL-based builds over committing full Vivado projects
- Commit only:
  - HDL source files
  - Constraints
  - Custom IP source code
  - Final `.bit` and `.hwh` needed to run the demo
- Do not commit generated IP output or cache folders

Goal: the design should be reproducible, not archived.

---

## 5. ESP32 Rules

- Use standard toolchains (PlatformIO preferred)
- Document board-specific setup in `wand/esp32/README.md`
- Do not commit build artifacts (`.pio/`, `.elf`, `.bin`)

---

## 6. Pull Request Requirements

All changes must be submitted via Pull Request.

Each PR should include:
- A brief description of the change
- Which subsystem it affects
- How it was tested
- Any known limitations

Small, focused PRs are preferred.

---

## 7. Testing Expectations

- Backend changes should include or update tests when possible
- Protocol changes must update schemas and examples
- FPGA and embedded changes must document validation steps

Testing should be intentional and documented.

---

## 8. Style and Code Quality

- Keep commits readable and focused
- Avoid committing commented-out or dead code
- Write code that another team member can understand

---

## 9. Communication

If something is unclear:
- Ask in the group chat
- Or open a GitHub Issue

By contributing to this repository, you agree to follow this guide.


