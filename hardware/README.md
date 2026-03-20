# Hardware

This directory contains the physical build-side documentation for the project.

## What To Expect Here

This subtree is intentionally lighter than `FPGA/` and `software/`, because the
main engineering depth of the final system sits in the node runtime and cloud
service. Use `hardware/` for physical context:

- what the wand looked like
- how the camera was positioned
- how the physical setup supported reliable tracking

## Subsystems

- [wand/](wand/)
  the physical wand implementation used by the final system.
- [camera/](camera/)
  camera-side mounting, placement, and sensing notes.

## Relationship To The Rest Of The Repo

- [FPGA/](../FPGA/)
  contains the programmable-logic design artefacts and PYNQ runtime code.
- [software/](../software/)
  contains the EC2 cloud service, protocols, and software-side tools.

Use this folder to present what was physically built, rather than the code that
ran on top of it.
