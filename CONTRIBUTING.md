# Contributing Guide

This repository contains the group coursework project for
**Information Processing – Group 10**.

The system spans multiple layers:
- Hardware notes and physical setup
- FPGA / Vivado hardware and PYNQ runtime
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
- `feature/hardware-camera-mount`
- `feature/fpga-dma-filter`
- `feature/backend-leaderboards`
- `feature/protocol-v1`
---

## 2. Repository Structure and Ownership

Please place files only in their intended locations.

### Wand / Edge Node
- `hardware/`
  physical build notes for the LED wand and camera setup

- `FPGA/`
  FPGA-related work:
  - `designs/` → Vivado exports, IP sources, screenshots, reports
  - `runtime/` → PYNQ / node-side software

### Cloud
- `software/cloud/backend/` → API and session logic
- `software/cloud/database/` → schema and persistence models
- `software/cloud/infra/` → deployment notes and infrastructure helpers

### Shared
- `software/protocol/` → message schemas and examples
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

## 5. Hardware Notes

- Keep physical build notes under `hardware/`
- Do not commit large raw media dumps; prefer selected photos, diagrams, and
  concise setup notes
- If a hardware concept was not part of the final integrated system, do not
  treat it as a required path in active documentation

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
