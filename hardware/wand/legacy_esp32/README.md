# Legacy ESP32 Wand Notes

This folder holds the original ESP32-side firmware concept for the wand.

## Current Status

The actively demonstrated end-to-end system ultimately used the camera +
PYNQ/FPGA path with a simpler physical LED wand instead of this ESP32 concept.

The ESP32 material is kept for:

- hardware context
- historical design reference
- button / auxiliary wand-event experiments

## Firmware

The current Arduino sketch lives at:

- [firmware/src/UDP_ESP_WAND.ino](firmware/src/UDP_ESP_WAND.ino)

## Recommendation

Treat this folder as supporting material rather than the final hardware used in
the integrated demo.
