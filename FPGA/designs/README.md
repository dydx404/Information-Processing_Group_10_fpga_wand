# FPGA Design Archive

This folder is for the hardware-design side of the PYNQ / FPGA subsystem.

It is intentionally separate from the Python notebook/runtime files in
[../](../) so the repo can present:

- the design currently used in the live system
- a fallback version of that design
- space for a teammate's alternative design work

## Layout

- [centroid_pipeline/](centroid_pipeline/)
  current centroid-based design family used by the live system.
- [teammate_design/](teammate_design/)
  reserved slot for a second design track.

## Per-Version Conventions

Each version folder is split into:

- `source/`
  HDL, block-design Tcl, IP configuration exports, or any source artefacts
  needed to recreate the design.
- `constraints/`
  XDC constraints and board-specific pin/timing files.
- `export/`
  generated handoff artefacts you intentionally want to keep, such as `.bit`,
  `.hwh`, `.xsa`, or packaged deliverables.
- `docs/`
  design notes, architecture summaries, and implementation rationale.
- `reports/`
  timing, utilization, and synthesis/implementation reports worth preserving.
- `images/`
  screenshots, block diagrams, or presentation visuals.

## Suggested Usage

- Put the design you actually demonstrated into `centroid_pipeline/used_version`.
- Put the simpler or safer backup build into `centroid_pipeline/fallback_version`.
- Let your teammate populate `teammate_design/` with another architecture or
  implementation approach.

If you later want more specific names, you can rename these top-level design
folders without changing the rest of the structure.
