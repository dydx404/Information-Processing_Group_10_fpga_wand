# PS / PL Signal And Control Flow

This note explains how the deployed PYNQ runtime and the used PL design work
together. It is based on the actual code in:

- [`pynq_wand_brain_demo.py`](./pynq_wand_brain_demo.py)
- [`pynq_udp_bridge.py`](./pynq_udp_bridge.py)
- [`../designs/centroid_pipeline/used_version/source/frame_centroid.v`](../designs/centroid_pipeline/used_version/source/frame_centroid.v)

## Design Intent

The project does not use the PL to perform the entire vision pipeline. The PS
and PL are split deliberately:

- the PS handles camera capture, image preprocessing, system control, local
  sketching, and networking
- the PL performs the regular per-pixel reduction step that is expensive to do
  repeatedly in software

The reduction result is a compact statistical summary of the frame rather than
another image stream.

## Startup Sequence

At startup, the PS performs these steps:

1. Load the bitstream with `Overlay(BIT)`.
2. Inspect `ol.ip_dict` and locate the DMA and centroid IP instances.
3. Open an AXI-Lite MMIO window for the centroid IP.
4. Allocate a flat DMA buffer of size `H * W`.
5. Open and warm up the camera.
6. Create the `WandBrainUdpBridge` for UDP data transmission and HTTP control.
7. Call the backend health endpoint.
8. Fetch the initial node-control payload and apply it before entering the main
   loop.

This means the PS establishes both the PL path and the cloud path before it
starts drawing.

## Signal Flow: Camera To PL

For every loop iteration, the PS starts with a camera frame:

1. `cap.read()` returns a BGR frame from the USB camera.
2. `preprocess_frame(...)` converts it to grayscale.
3. The frame is resized to `640 x 480`.
4. A Gaussian blur is applied to suppress small pixel noise.
5. A binary threshold is applied, producing an 8-bit foreground mask where
   bright pixels become `255` and dark pixels become `0`.

The preprocessed frame is then sent into the PL:

1. The binary image is flattened into the DMA buffer.
2. `dma.sendchannel.transfer(buf)` starts the AXI DMA transfer.
3. `dma.sendchannel.wait()` blocks until the full frame has been streamed.

Architecturally, this is a one-way memory-to-stream path:

- the PS writes the frame into DDR-backed memory
- the DMA reads from memory
- the custom IP consumes an AXI4-Stream

There is no stream coming back from the PL. The result returns through
registers.

## Signal Flow Inside The PL

The custom module `frame_centroid` consumes the DMA stream through:

- `s_axis_tdata[31:0]`
- `s_axis_tvalid`
- `s_axis_tready`
- `s_axis_tlast`

The important implementation details are:

1. `s_axis_tready` is hard-wired to `1`, so the IP is always willing to accept
   data.
2. Each 32-bit AXI beat carries four 8-bit grayscale pixels.
3. The module unpacks those four pixels as `p0..p3`.
4. It associates them with four x-coordinates `x0..x3`.
5. Each pixel is tested against `THRESHOLD`.
6. For bright pixels only, the module increments:
   - `bright_count`
   - `sum_x`
   - `sum_y`
7. The internal `x` counter advances by four pixels per beat.
8. When the end of a row is reached, `x` wraps to zero and `y` increments.
9. A frame ends when either:
   - `s_axis_tlast` is asserted, or
   - the expected `WIDTH * HEIGHT` pixels have been consumed
10. At frame end, the module latches:
   - `o_sum_x`
   - `o_sum_y`
   - `o_count`
   - `o_frame_id`
   - `o_valid`
11. The running accumulators are then reset for the next frame.

In the deployed pipeline, the PS already sends a binary image. That means the
PL threshold test is effectively selecting the `255` foreground pixels.

## Signal Flow: PL Back To The PS

After the DMA transfer completes, the PS reads the centroid IP registers using
MMIO:

- `0x00` / `0x04`: `sum_x`
- `0x08` / `0x0C`: `sum_y`
- `0x10`: `count`
- `0x14`: `frame_id`
- `0x18`: `valid`

The PS reconstructs the 40-bit sums and computes:

- `cx = sum_x // count`
- `cy = sum_y // count`

This is an intentional boundary:

- the PL provides raw statistics
- the PS performs the division and all later policy decisions

## Freshness And Duplicate Handling

One subtle but important detail is that the HDL sets `o_valid <= 1'b1` when a
frame completes, but it does not clear `o_valid` again until reset. In other
words, `valid` behaves like a sticky "results available" flag, not a one-cycle
fresh-data pulse.

Because of that, the PS does not rely on `valid` alone. It also tracks
`frame_id`:

- `new_result = (frame_id != last_frame_id)`

This lets the runtime distinguish:

- a genuinely new hardware result
- a repeated read of the same latched result

That detail matters again in the UDP sender. The bridge stores the
`last_sent_frame_id`, and if the PS sees the same hardware result again, it
returns `hold_duplicate` instead of sending another point packet. This prevents
duplicate network points while still keeping the current stroke alive.

## Runtime Control Flow On The PS

The PS loop is not just a passive reader of PL output. It is the main control
plane of the node.

The runtime maintains:

- `runtime_state`
  current applied control values such as threshold, min-count, gap timeout, and
  mode
- `drawing_state`
  local sketch canvas and previous point history
- `pending_control`
  a control revision that was received but intentionally delayed

Every `CONTROL_POLL_INTERVAL_MS`, the PS:

1. polls `/api/v3/node/{device}/control`
2. merges the payload into effective settings
3. either applies the new revision immediately, or queues it until the active
   stroke has ended

This `apply_on` behavior is important:

- `immediate` means the control change is safe to apply now
- `next_attempt` means the runtime waits until the node is idle so an active
  stroke is not corrupted halfway through

The PS also posts periodic acknowledgements back to the server, including:

- applied revision
- whether a stroke is active
- whether transmission is active
- pending revision
- last error, if any

## Per-Frame Decision Flow

Once the current centroid statistics are available, the PS makes a series of
gating decisions.

### 1. Hardware-level validity

The PS forms:

- `valid_hw = bool(stats["valid"]) and stats["count"] >= min_count`

So the PL says "a frame result exists", and the PS adds the stronger policy
that the blob must contain enough bright pixels.

### 2. Node-level enable state

The PS forms:

- `tracking_enabled = enabled and armed`

This is how the server can control the board without changing the bitstream:

- `enabled = false` blocks tracking completely
- `armed = false` keeps the node alive but prevents normal stroke operation
- `tx_enabled = false` allows local logic to keep running but blocks upstream
  UDP transmission

### 3. UDP emission decision

The PS forms:

- `valid_for_udp = tracking_enabled and tx_enabled and valid_hw`

If this is true, the centroid is handed to `bridge.process_point(...)`.

The bridge then performs the network-side stroke state machine:

- start a new stroke on the first valid point after idle
- send one UDP packet for each valid point
- normalize pixel coordinates to `[0, 1]`
- convert them to Q15 integers
- set `PEN_DOWN`, `STROKE_START`, or `STROKE_END`
- end the stroke after `gap_timeout_ms` without a valid point

This means the PS decides whether a point is acceptable, while the bridge
decides how that accepted point should be packetized as part of a stroke.

### 4. Local sketch decision

Separately, the PS forms:

- `valid_for_sketch = tracking_enabled and new_result and valid_hw`

So the local notebook sketch is intentionally tied to fresh hardware results.
That avoids drawing the same latched centroid repeatedly.

When a sketch point is accepted, the PS:

1. mirrors the x-coordinate for presentation
2. maps the centroid from camera coordinates into sketch coordinates
3. smooths the point using `smoothing_alpha`
4. rejects implausibly large jumps using `max_jump`
5. draws either:
   - a line from the previous accepted point, or
   - an isolated point if no line is appropriate

## Server-Controlled Behavior

The interesting control features live almost entirely in the PS rather than the
PL. The server can influence:

- `threshold`
- `min_count`
- `gap_timeout_ms`
- `max_jump`
- `smoothing_alpha`
- `enabled`
- `armed`
- `tx_enabled`
- mode selection such as `normal`, `precision`, `fast`, and `noisy_room`

One-shot command tokens can also trigger:

- sketch clearing
- threshold recalibration using fresh camera frames

This is a key architectural choice of the final system:

- the PL stays stable and focused on frame reduction
- the PS remains flexible and can change behavior live through HTTP control

## Why This Split Worked Well

This PS/PL boundary was a good fit for the project because:

- the most repetitive per-pixel operation moved into hardware
- the PS still had full freedom to tune thresholds and stroke logic
- integration with the camera and the EC2 backend stayed simple
- debugging was manageable because the PL output was small and interpretable
- the cloud control path could change runtime behavior without requiring a new
  FPGA bitstream

In short, the PL acts as a centroid-statistics accelerator, while the PS acts
as the node controller.
