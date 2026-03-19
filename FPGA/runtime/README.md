# PYNQ Runtime

Use [pynq_udp_bridge.py](pynq_udp_bridge.py) to send centroid points from a
PYNQ notebook or script to Wand Brain.

## Repository Layout

- runtime integration code stays directly in [./](.)
- hardware design artefacts live under [../designs/](../designs/)

That split keeps the repo easier to present:

- software/runtime logic in one place
- Vivado/export/design evidence in another

## What It Does

- keeps the camera + DMA + MMIO centroid pipeline unchanged
- performs an HTTP preflight check against Wand Brain
- sends one `wb-point-v1` UDP packet per valid centroid point
- starts a new stroke on the first valid point after idle
- sends one explicit `STROKE_END` packet after a short no-blob gap

## Deep Dive

For the actual deployed signal path and control decisions, see
[ps_pl_flow.md](ps_pl_flow.md). That document walks through:

- camera frame preprocessing on the PS
- DMA transfer into the custom centroid IP
- register readback from the PL
- fresh-result detection using `frame_id`
- UDP stroke generation
- server-driven node control and acknowledgements

## Minimal Notebook Pattern

```python
import sys
sys.path.append("/home/xilinx/Information-Processing_Group_10_fpga_wand")

from FPGA.runtime.pynq_udp_bridge import WandBrainConfig, WandBrainUdpBridge

bridge = WandBrainUdpBridge(
    WandBrainConfig(
        brain_host="13.51.156.87",
        brain_udp_port=41000,
        brain_api_port=8000,
        device_number=1,
        wand_id=1,
        starting_stroke_id=1,
        gap_timeout_ms=220,
        mirror_x=True,
    )
)

print(bridge.preflight_check())
```

## Notes

- Set `brain_host` to the current EC2 public IP. In the main demo script this
  can be overridden with the `BRAIN_HOST` environment variable.
- `timestamp_ms=None` means the bridge uses local monotonic milliseconds.
- `mirror_x=True` makes backend rendering match the mirrored local sketch view.
- The bridge sends explicit `STROKE_END`, which is compatible with both older
  and newer Wand Brain builds.
- For the centroid notebook demo, prefer `MIN_COUNT_TO_ACCEPT >= 4` and
  `VALID_STREAK_REQUIRED >= 2` to suppress single-pixel flicker and one-frame
  false starts.
