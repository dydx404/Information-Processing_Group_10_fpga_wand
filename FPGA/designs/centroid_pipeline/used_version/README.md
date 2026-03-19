# Used Version

This folder is for the FPGA build that was actually used in the working system.

Recommended contents:

- source design files in `source/`
- `.xdc` files in `constraints/`
- exported `.bit`, `.hwh`, `.xsa`, or equivalent artefacts in `export/`
- implementation notes in `docs/`
- timing / utilization reports in `reports/`
- block-diagram screenshots in `images/`

Good things to include in `docs/`:

- the register map exposed to the PS
- the main IP blocks used
- why this version was chosen over the fallback
- known limitations or tradeoffs
