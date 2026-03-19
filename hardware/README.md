# Hardware

This directory contains the physical build-side documentation for the project.

## Subsystems

- [wand/](wand/)
  the physical wand implementations, including the final 3D-printed LED wand
  and the older ESP32 concept.
- [camera/](camera/)
  camera-side mounting, placement, and sensing notes.

## Relationship To The Rest Of The Repo

- [FPGA/](../FPGA/)
  contains the programmable-logic design artefacts and PYNQ runtime code.
- [software/](../software/)
  contains the EC2 cloud service, protocols, and software-side tools.

Use this folder to present what was physically built, rather than the code that
ran on top of it.
