# FPGA

This directory contains the FPGA-side implementation of the project.

## Main Areas

- [runtime/](runtime/)
  PYNQ-side Python runtime used to bridge the camera/centroid pipeline to the
  Wand Brain cloud service.
- [designs/](designs/)
  archived hardware design artefacts, including the version used in the final
  system and fallback versions.

## Suggested Tour

Start here if you want to present the FPGA contribution clearly:

1. [runtime/pynq_wand_brain_demo.py](runtime/pynq_wand_brain_demo.py)
2. [runtime/pynq_udp_bridge.py](runtime/pynq_udp_bridge.py)
3. [designs/README.md](designs/README.md)
4. [designs/centroid_pipeline/used_version/README.md](designs/centroid_pipeline/used_version/README.md)
