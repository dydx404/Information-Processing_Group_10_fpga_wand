# PYNQ UDP Transmission, Receive, And Parse Flow

This note explains the full `wb-point-v1` path from the PYNQ board to Wand
Brain. It complements the packet contract in
[`pynq-udp-brian-v1.md`](./pynq-udp-brian-v1.md) by showing how the protocol is
actually used in the deployed system.

The main implementation files are:

- PYNQ sender and runtime gating:
  [`../../../FPGA/runtime/pynq_wand_brain_demo.py`](../../../FPGA/runtime/pynq_wand_brain_demo.py)
- PYNQ UDP bridge:
  [`../../../FPGA/runtime/pynq_udp_bridge.py`](../../../FPGA/runtime/pynq_udp_bridge.py)
- cloud UDP receiver:
  [`../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py)
- cloud packet parser:
  [`../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py)
- cloud state machine:
  [`../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)

## Contract Summary

The protocol spec already defines the wire-level contract:

> **Direction:** PYNQ -> Wand Brain  
> **Protocol name:** `wb-point-v1`  
> **Transport:** UDP  
> **Packet size:** 24 bytes fixed  
> **Endianness:** little-endian

The spec also defines the sender-side stroke semantics:

> first valid point after idle => `STROKE_START | PEN_DOWN`  
> middle valid points => `PEN_DOWN`  
> one final packet after the stroke ends => `STROKE_END`

Those two short quotes are the whole idea of the data plane:

- one UDP datagram carries one point sample
- the packet flags describe where that point sits in the stroke lifecycle

## Why UDP Is Used Here

The project uses UDP as a low-latency point-stream transport rather than a
reliable byte stream.

That matches the system architecture well:

- the board sends frequent, small, independent point updates
- the backend can tolerate occasional packet loss better than retransmission
  delay
- the stroke lifecycle is expressed explicitly with packet flags
- the control plane is handled separately over HTTP, so the UDP path can stay
  narrow and fast

In this design:

- UDP is the drawing data plane
- HTTP is the control and monitoring plane

## Stage 1: PS Decides Whether A Centroid Becomes A Network Point

The PS runtime does not transmit every camera frame. It first decides whether
the current hardware result is good enough to be used.

In [`pynq_wand_brain_demo.py`](../../../FPGA/runtime/pynq_wand_brain_demo.py),
the runtime:

1. captures a camera frame
2. preprocesses it into a binary image
3. streams that frame into the PL through AXI DMA
4. reads back the centroid statistics through MMIO
5. computes the centroid in software
6. decides whether the result is valid for sketching and/or UDP

The key gating values are:

- `valid_hw`
  true only if the hardware result is marked valid and the bright-pixel count
  is at least `min_count`
- `tracking_enabled`
  true only if the node is both `enabled` and `armed`
- `valid_for_udp`
  true only if tracking is enabled, transmission is enabled, and the hardware
  result passed the software acceptance test

So the PS performs policy before networking. The PL provides centroid
statistics, but the PS decides whether those statistics should become a point on
the wire.

## Stage 2: PYNQ Sender Builds A Stroke

The stateful network sender is
[`pynq_udp_bridge.py`](../../../FPGA/runtime/pynq_udp_bridge.py).

Its job is not just "send one packet". It also manages stroke lifecycle.

### Bridge Configuration

The bridge is configured with:

- `brain_host`
- `brain_udp_port`
- `brain_api_port`
- `device_number`
- `wand_id`
- `starting_stroke_id`
- `starting_packet_number`
- `gap_timeout_ms`
- optional `mirror_x` and `mirror_y`

These fields split into two groups:

- transport and identity:
  `brain_host`, `brain_udp_port`, `device_number`, `wand_id`
- stroke behavior:
  `starting_stroke_id`, `starting_packet_number`, `gap_timeout_ms`

### Coordinate Normalization

The PS passes centroid coordinates into the bridge in pixel units:

- `x_px`
- `y_px`
- `src_w`
- `src_h`

The bridge converts those into normalized coordinates:

- `x = x_px / (src_w - 1)`
- `y = y_px / (src_h - 1)`

Optional mirroring is applied here, not in the protocol parser:

- `mirror_x` flips the normalized x coordinate
- `mirror_y` flips the normalized y coordinate

After that, the bridge converts the normalized coordinates into Q15 integers:

- `x_q = round(x * 32767)`
- `y_q = round(y * 32767)`

That matches the protocol spec exactly and makes the packet independent of the
camera resolution.

### Stroke State Machine On The Board

The sender keeps internal state:

- `packet_number`
- `next_stroke_id`
- `active_stroke_id`
- `last_valid_ms`
- `last_valid_q15`
- `last_sent_frame_id`
- `sent_points_in_stroke`

This allows it to interpret a stream of accepted centroid points as a stroke.

The runtime calls:

```python
bridge.process_point(
    valid=valid_for_udp,
    x_px=stats["cx"] if valid_for_udp else None,
    y_px=stats["cy"] if valid_for_udp else None,
    src_w=W,
    src_h=H,
    timestamp_ms=None,
    frame_id=frame_id,
)
```

From there, the sender behavior is:

1. If the current point is valid and there is no active stroke:
   - allocate a new `stroke_id`
   - send a packet with `STROKE_START | PEN_DOWN`
2. If the point is valid and a stroke is already active:
   - send a packet with `PEN_DOWN`
3. If there has been no valid point for at least `gap_timeout_ms`:
   - send one final packet with `STROKE_END`
   - close the sender-side stroke

This is how "wand visible now" gets turned into a structured stroke over UDP.

### Duplicate Hardware Result Suppression

There is one subtle but important sender behavior.

The PL `valid` flag is effectively sticky after a completed frame, so the PS
may re-read the same hardware result multiple times. To avoid sending duplicate
network points, the sender tracks `last_sent_frame_id`.

If:

- the point is valid
- a stroke is already active
- the same `frame_id` is seen again

then the bridge returns `hold_duplicate` and does not emit a new packet.

However, it still updates `last_valid_ms`, which keeps the stroke alive.

This is a good example of where the board-side sender logic and the hardware
interface are tightly coupled.

## Stage 3: Packet Layout On The Wire

The binary packet format is defined in
[`pynq-udp-brian-v1.md`](./pynq-udp-brian-v1.md).

The sender and parser both use the same struct layout:

```text
<HBBHHIIhhI
```

That expands to:

1. `uint16 magic`
2. `uint8 version`
3. `uint8 flags`
4. `uint16 device_number`
5. `uint16 wand_id`
6. `uint32 packet_number`
7. `uint32 stroke_id`
8. `int16 x_q`
9. `int16 y_q`
10. `uint32 timestamp_ms`

The bridge packs that structure using:

```python
WB_STRUCT.pack(
    WB_MAGIC,
    WB_VERSION,
    flags,
    self.cfg.device_number,
    self.cfg.wand_id,
    self.packet_number,
    stroke_id,
    x_q,
    y_q,
    timestamp_ms & 0xFFFFFFFF,
)
```

The important field meanings in the deployed system are:

- `device_number`
  identifies the physical PYNQ board
- `wand_id`
  identifies the wand / player
- `packet_number`
  is monotonic per sender instance
- `stroke_id`
  identifies the source-side stroke
- `timestamp_ms`
  is the sender timestamp truncated to 32 bits

The backend intentionally does **not** treat `stroke_id` as a guaranteed global
attempt identifier. It is treated as source metadata.

## Stage 4: Raw UDP Reception On The Server

The cloud-side receive loop lives in
[`udp_rx.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py).

The `UdpReceiver`:

- creates a UDP socket
- binds to `0.0.0.0:41000`
- sets a receive timeout
- loops in a background thread
- calls `recvfrom(...)`
- stores the latest raw packet and source address
- forwards the raw packet to a callback

This module is deliberately thin. It does not parse or interpret the packet. It
is just the socket ingress layer.

## Stage 5: Packet Parsing

The packet parser lives in
[`parser.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py).

Its job is:

- validate the binary packet
- unpack the fields
- convert them into a typed `PointEvent`

### Validation Rules

For the `wb-point-v1` path, the parser rejects a packet if:

- length is not exactly `24`
- `magic` is not `0x5742`
- `version` is not `1`
- `x_q` or `y_q` is outside `0..32767`

If all checks pass, the parser constructs a `PointEvent` containing:

- `device_number`
- `wand_id`
- `stroke_id`
- `packet_number`
- `x`
- `y`
- `timestamp_ms`
- `flags`
- `pen_down`
- `stroke_start`
- `stroke_end`

The numeric coordinates are converted back to normalized floats:

- `x = x_q / 32767.0`
- `y = y_q / 32767.0`

So the parser is the boundary between:

- raw bytes on the socket
- semantic events for the backend state machine

### Legacy CSV Fallback

The parser still contains an optional legacy CSV fallback for development:

- `x,y,t,wand`

That is not the primary deployed path for the current system. The final PYNQ
integration uses the fixed-size binary format.

## Stage 6: Parsed Event To Live Attempt

Once a packet is parsed successfully, the receive callback in
[`server.py`](../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
calls:

```python
ev = parse_packet(raw)
if ev is None:
    return
state.on_event(ev)
```

This is where the parser stops and the application logic starts.

The `BrainState` object then:

1. finalizes stale idle attempts if needed
2. records the latest event
3. ensures a `WandStatus` exists for the given `wand_id`
4. decides whether the packet is point-like
5. resolves which internal attempt the event belongs to
6. appends the point into the live attempt buffer
7. finalizes the attempt if `stroke_end` is set

### Why The Backend Has Internal Attempt IDs

The source packet contains `stroke_id`, but the server does not rely on that as
the permanent database identity.

Instead:

- `stroke_id` is preserved as `source_stroke_id`
- the backend generates its own internal `attempt_id`

This avoids collisions when:

- a sender restarts
- `stroke_id` values are reused
- multiple sessions occur over time

This distinction is one of the most important things to understand in the
current Wand Brain backend.

### Attempt Resolution

The backend keeps a `WandStatus` per wand. When a new point arrives, it uses
the current `wand_id`, `device_number`, active attempt state, and
`source_stroke_id` to decide whether the point belongs to:

- the currently active internal attempt, or
- a newly allocated internal attempt

If an active attempt is replaced unexpectedly, the server finalizes the old one
with `close_reason="attempt_replaced"`.

## Stage 7: Stroke Finalization

The server can finalize a stroke in two ways.

### Explicit Finalization

If the packet has `stroke_end = True`, the backend finalizes the current
attempt immediately with:

- `close_reason = "explicit_end"`

This corresponds to the board sending the final `STROKE_END` packet.

### Idle Finalization

The server also runs an idle finalizer thread. If packets stop arriving for an
active attempt and the idle timeout expires, the attempt is finalized with:

- `close_reason = "idle_timeout"`

This is a safety mechanism in case:

- the sender stops unexpectedly
- the end packet is not seen
- the stroke just naturally fades out without another point

### Tiny Fragment Discard

If an idle-finalized attempt contains fewer than the configured minimum number
of points, the backend discards it instead of keeping it as a real result.

That behavior is important because it suppresses tiny accidental fragments caused
by noise or one-frame false starts.

## Stage 8: Live Render And Final Output

Although this note focuses on transmission and parsing, the last step is useful
to understand because it shows why the UDP path exists in the first place.

As points are appended to an attempt buffer, the backend periodically rasterizes
them into a live PNG for the website. When the attempt is finalized, the server:

- renders a final PNG
- stores final metadata
- exposes that attempt through HTTP endpoints

So the full chain is:

1. centroid accepted on the board
2. UDP packet emitted
3. raw datagram received on port `41000`
4. binary packet parsed into a `PointEvent`
5. point appended to the live attempt buffer
6. live and final drawings rendered from the point list

## End-To-End Summary

The cleanest way to describe the current UDP path is:

1. The PS decides whether the current centroid is good enough to transmit.
2. The PYNQ bridge normalizes the centroid, manages stroke state, and packs one
   `wb-point-v1` packet per point.
3. The server-side UDP receiver accepts raw datagrams on port `41000`.
4. The parser validates the 24-byte packet and converts it into a `PointEvent`.
5. The backend state machine reconstructs attempts from those events, finalizes
   them on `STROKE_END` or idle timeout, and exposes the results to the web
   application.

That means the UDP protocol is not just a byte layout. It is the contract
between:

- PS-side centroid tracking and stroke emission
- cloud-side live attempt reconstruction

Both halves matter for the system to behave correctly.
