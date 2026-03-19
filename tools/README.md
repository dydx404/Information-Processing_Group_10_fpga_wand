# Tools

This folder contains helper scripts for local testing, observable demos, and
operator checks.

## Most Useful Scripts

- [start_brain_server.sh](start_brain_server.sh)
  wrapper that starts the canonical cloud app.
- [wb_connection_check.py](wb_connection_check.py)
  quick health + UDP connectivity check against a Wand Brain instance.
- [full_system_smoke_test.py](full_system_smoke_test.py)
  end-to-end UDP-to-API smoke test that verifies finalization and rendering.
- [run_observable_udp_demo.sh](run_observable_udp_demo.sh)
  demo helper for visible packet-to-dashboard runs.
- [run_observable_long_stroke_demo.sh](run_observable_long_stroke_demo.sh)
  longer observable stroke demo against the live service.
- [fake_wb_sender.py](fake_wb_sender.py)
  low-level synthetic sender for protocol-level debugging.

## Usage Principle

These scripts are for validation and demos. They are not the canonical runtime
itself; that lives under [cloud/](../cloud/) and [wand/](../wand/).
