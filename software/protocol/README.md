# Protocols

This directory contains the explicit interface contracts used across the
project.

## Current Important Specs

- [protocol/pynq-udp-brian-v1.md](protocol/pynq-udp-brian-v1.md)
  defines the fixed-size UDP point-stream packet from PYNQ to Wand Brain.
- [protocol/brain-web_api.md](protocol/brain-web_api.md)
  summarizes the HTTP APIs used by the frontend, control plane, and database
  views.
- [protocol/esp-wand_protocol.md](protocol/esp-wand_protocol.md)
  documents the original ESP32 button-event concept for the wand side.

## Design Principle

The protocol docs are the contract boundary between subsystems. The packet
format should remain stable unless all affected owners agree to the change.
