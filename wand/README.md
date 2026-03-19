# Wand Nodes

This directory contains the node-side code for the project.

## Subsystems

- [fpga/](fpga/)
  current PYNQ / FPGA notebooks and Python helpers used to capture centroid
  data, package UDP points, and poll HTTP node control.
- [esp32/](esp32/)
  original ESP32-side firmware and notes for the wand hardware concept.

## Architectural Role

The wand node is where sensing and low-latency point generation happen:

- PL accelerates centroid-style bright-pixel reduction.
- PS software handles preprocessing, validity decisions, sketching, UDP
  transmission, and HTTP control polling.

If you are working on the currently demonstrated system, start in
[fpga/](fpga/).
