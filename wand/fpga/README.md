# PYNQ / FPGA Notebook Integration

Use `wand/fpga/pynq_udp_bridge.py` to send centroid points from a PYNQ notebook to Wand-Brain.

## What It Does

- keeps the existing camera + DMA + MMIO centroid pipeline unchanged
- performs an HTTP preflight check against Wand-Brain
- sends one `wb-point-v1` UDP packet per valid centroid point
- starts a new stroke on the first valid point after idle
- sends one explicit `STROKE_END` packet after a short no-blob gap

## Minimal Notebook Pattern

```python
import sys
sys.path.append("/home/xilinx/Information-Processing_Group_10_fpga_wand")

from wand.fpga.pynq_udp_bridge import WandBrainConfig, WandBrainUdpBridge

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

Inside the frame loop:

```python
centroid_ready = stats["count"] >= MIN_COUNT_TO_ACCEPT and stats["valid"] == 1

if new_result and centroid_ready:
    valid_streak += 1
elif new_result:
    valid_streak = 0

valid = new_result and centroid_ready and valid_streak >= VALID_STREAK_REQUIRED

udp_debug = bridge.process_point(
    valid=valid,
    x_px=stats["cx"] if valid else None,
    y_px=stats["cy"] if valid else None,
    src_w=W,
    src_h=H,
    timestamp_ms=None,
    frame_id=stats["frame_id"],
)
```

During cleanup:

```python
bridge.flush()
bridge.close()
```

## Notes

- Set `brain_host` to the current EC2 public IP. In the main demo script this can now be overridden with the `BRAIN_HOST` environment variable.
- `timestamp_ms=None` means the bridge uses local monotonic milliseconds.
- `mirror_x=True` makes backend rendering match the mirrored local sketch view.
- The bridge sends explicit `STROKE_END`, which is compatible with both older and newer Wand-Brain builds.
- For the centroid notebook demo, prefer `MIN_COUNT_TO_ACCEPT >= 4` and `VALID_STREAK_REQUIRED >= 2` to suppress single-pixel flicker and one-frame false starts.
