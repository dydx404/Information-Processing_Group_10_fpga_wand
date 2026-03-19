# Wand Brain UDP Input Protocol

**Direction:** PYNQ -> Wand Brain  
**Protocol name:** `wb-point-v1`  
**Transport:** UDP  
**Packet size:** 24 bytes fixed  
**Endianness:** little-endian

This protocol is the low-latency point-stream data plane used by the PYNQ node
to send centroid-derived drawing points to the cloud backend.

## Packet Layout

Struct format:

```text
<HBBHHIIhhI
```

Field order:

| Offset | Size | Type | Field | Description |
|------:|----:|------|-------|-------------|
| 0 | 2 | `uint16` | `magic` | Constant `0x5742` (`WB`) |
| 2 | 1 | `uint8` | `version` | Must be `1` |
| 3 | 1 | `uint8` | `flags` | Bitfield |
| 4 | 2 | `uint16` | `device_number` | PYNQ board identifier |
| 6 | 2 | `uint16` | `wand_id` | Wand identifier |
| 8 | 4 | `uint32` | `packet_number` | Monotonic packet sequence |
| 12 | 4 | `uint32` | `stroke_id` | Source-side stroke identifier |
| 16 | 2 | `int16` | `x_q` | Q15 normalized x in `0..32767` |
| 18 | 2 | `int16` | `y_q` | Q15 normalized y in `0..32767` |
| 20 | 4 | `uint32` | `timestamp_ms` | Sender timestamp, low 32 bits |

## Flags

| Bit | Mask | Name | Meaning |
|---:|:---:|------|---------|
| 0 | `0x01` | `PEN_DOWN` | Point belongs to an active stroke |
| 1 | `0x02` | `STROKE_START` | First emitted point of a stroke |
| 2 | `0x04` | `STROKE_END` | Final emitted packet of a stroke |

## Coordinate Encoding

Coordinates are normalized before transmission and encoded as Q15 integers:

- `x_q = round(x_norm * 32767)`
- `y_q = round(y_norm * 32767)`

Valid transmitted range is:

- `0 .. 32767`

This makes the packet resolution-independent.

## Sender-Side Semantics

The PYNQ sender is stateful:

- first valid point after idle => `STROKE_START | PEN_DOWN`
- middle valid points => `PEN_DOWN`
- one final packet after the stroke ends => `STROKE_END`

The sender should keep:

- `device_number` stable per board
- `wand_id` stable per wand
- `packet_number` monotonic per sender
- `stroke_id` stable for one source-side stroke

## Backend-Side Semantics

`stroke_id` is treated as a **source stroke identifier**, not a guaranteed
globally unique database attempt identifier.

The backend may assign its own internal `attempt_id` when finalizing attempts so
that restarts or reused source IDs do not collide with persisted history.

In API responses, this typically appears as:

- `attempt_id`: backend-owned identifier
- `source_stroke_id`: original UDP `stroke_id`

## Validation Rules

A packet is rejected if:

- length is not 24 bytes
- `magic != 0x5742`
- `version != 1`
- `x_q` or `y_q` is outside `0..32767`

## Reference C Struct

```c
#pragma pack(push, 1)
typedef struct {
  uint16_t magic;
  uint8_t  version;
  uint8_t  flags;
  uint16_t device_number;
  uint16_t wand_id;
  uint32_t packet_number;
  uint32_t stroke_id;
  int16_t  x_q;
  int16_t  y_q;
  uint32_t timestamp_ms;
} wb_point_v1_t;
#pragma pack(pop)
```
