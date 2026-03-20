# FPGA

This directory contains the FPGA-side implementation of the project.

## If You Open One File First

For most newcomers, start with:

- [runtime/ps_pl_flow.md](runtime/ps_pl_flow.md)

That document explains the final adopted PS/PL signal flow and points back to
the relevant runtime code and Vivado artefacts.

## Main Areas

- [runtime/](runtime/)
  PYNQ-side Python runtime used to bridge the camera/centroid pipeline to the
  Wand Brain cloud service.
- [designs/](designs/)
  archived hardware design artefacts, including the version used in the final
  system and fallback versions.

## PS / PL Architecture

The deployed board design is best understood as a split between:

- the PS as the runtime controller
- the PL as a centroid-statistics accelerator

At a high level, the signal flow is:

1. the PS captures a camera frame
2. the PS preprocesses it into a binary `640 x 480` image
3. the PS sends that image through AXI DMA into the custom centroid IP
4. the PL reduces the frame into `sum_x`, `sum_y`, `count`, `frame_id`, and
   `valid`
5. the PS reads those registers, computes the centroid, applies filtering and
   stroke logic, and sends accepted points to Wand Brain

The control flow is also PS-led:

- the PS polls node control over HTTP
- applies immediate or next-stroke configuration changes
- decides whether tracking is enabled
- decides whether a centroid is good enough to sketch or transmit
- manages the UDP stroke state machine through the runtime bridge

So the PL is intentionally narrow and stable, while the PS holds the policy,
integration, and live control behavior.

For the detailed step-by-step version, see
[runtime/ps_pl_flow.md](runtime/ps_pl_flow.md).

## Newcomer Route

If you are trying to understand the FPGA contribution quickly, read in this
order:

1. [runtime/ps_pl_flow.md](runtime/ps_pl_flow.md)
2. [runtime/pynq_wand_brain_demo.py](runtime/pynq_wand_brain_demo.py)
3. [runtime/pynq_udp_bridge.py](runtime/pynq_udp_bridge.py)
4. [designs/centroid_pipeline/used_version/README.md](designs/centroid_pipeline/used_version/README.md)
5. [designs/centroid_pipeline/used_version/source/frame_centroid.v](designs/centroid_pipeline/used_version/source/frame_centroid.v)

## Suggested Tour

Start here if you want to present the FPGA contribution clearly:

1. [runtime/pynq_wand_brain_demo.py](runtime/pynq_wand_brain_demo.py)
2. [runtime/pynq_udp_bridge.py](runtime/pynq_udp_bridge.py)
3. [runtime/ps_pl_flow.md](runtime/ps_pl_flow.md)
4. [designs/README.md](designs/README.md)
5. [designs/centroid_pipeline/used_version/README.md](designs/centroid_pipeline/used_version/README.md)
