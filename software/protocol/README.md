# Protocols

This directory contains the explicit interface contracts used across the
project.

## Current Important Specs

- [protocol/pynq-udp-brian-v1.md](protocol/pynq-udp-brian-v1.md)
  defines the fixed-size UDP point-stream packet from PYNQ to Wand Brain.
- [protocol/pynq-udp-flow.md](protocol/pynq-udp-flow.md)
  explains how the PYNQ sender, UDP receiver, parser, and backend state machine
  use that packet format end to end.
- [protocol/brain-web_api.md](protocol/brain-web_api.md)
  indexes the HTTP API families used by the frontend, control plane, scoring,
  leaderboard, and database views.
- [protocol/brain_api/README.md](protocol/brain_api/README.md)
  expands the Brain HTTP APIs into separate detailed guides by feature area.

## Design Principle

The protocol docs are the contract boundary between subsystems. The packet
format should remain stable unless all affected owners agree to the change.
