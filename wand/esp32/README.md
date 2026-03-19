# ESP32 Wand Notes

This folder holds the original ESP32-side firmware concept for the wand.

## Current Status

The actively demonstrated end-to-end system is driven by the PYNQ / FPGA path
under [../fpga/](../fpga/).

The ESP32 material is kept for:

- hardware context
- historical design reference
- button / auxiliary wand-event experiments

## Firmware

The current Arduino sketch lives at:

- [firmware/src/UDP_ESP_WAND.ino](firmware/src/UDP_ESP_WAND.ino)

## Recommendation

If you are preparing a demo or running the live cloud service, start with the
PYNQ sender and treat this folder as supporting material rather than the main
runtime path.
