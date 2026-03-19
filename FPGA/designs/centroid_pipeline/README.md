# Centroid Pipeline Design

This is the main FPGA design family used by the current wand demo flow.

It is split into:

- [used_version/](used_version/)
  the version currently used in the integrated system.
- [fallback_version/](fallback_version/)
  the backup version kept in case the main build is unstable or unsuitable for
  demo use.

Use this folder to present the evolution of your design clearly:

- what was actually deployed
- what was kept as a reliable fallback
- how the two versions differ
