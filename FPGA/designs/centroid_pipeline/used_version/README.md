# Used Version

This folder is for the FPGA build that was actually used in the working system.

Current contents:

- `source/frame_centroid.v`
  Core custom centroid-reduction HDL.
- `source/design_1_wrapper.tcl`
  Vivado-generated implementation / export script captured from the used build.
- `export/design_1_wrapper.bit`
  Bitstream used on the board.
- `export/design_1_wrapper.hwh`
  Hardware handoff metadata used by PYNQ.
- `images/top.png`
  Top-level block design screenshot.
- `images/timing.png`
  Timing summary screenshot for the implemented design.
- `docs/design_summary.md`
  Top-level architecture, data path, and design rationale.
- `docs/register_map.md`
  PS-visible register map used by the runtime.
- `docs/pl_exports.md`
  Short inventory of exported implementation artefacts.

Still useful to add later:

- timing and utilization reports in `reports/`
- any manually written constraint files in `constraints/`
- close-up screenshots of the custom IP, Address Editor, or DMA wiring
- a short note comparing this version against the fallback build
