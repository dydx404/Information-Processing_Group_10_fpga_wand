# Wand-Brain UDP Input Protocol  
**PYNQ Board → Wand-Brain (EC2)**  
**Protocol name:** `wb-point-v1`  
**Status:** MVP / frozen for team coordination

---

## 1. Transport

- **Protocol:** UDP
- **Direction:** PYNQ → Wand-Brain
- **One UDP datagram = one point sample**
- **Endianness:** Little-endian
- **Recommended port:** `41000`
- **Packet size:** **24 bytes (fixed)**

This protocol is intentionally simple, fixed-size, and binary for low latency and easy parsing.

---

## 2. Packet Layout (24 bytes)

| Offset | Size | Type | Field | Description |
|------:|----:|------|-------|-------------|
| 0 | 2 | `uint16` | `magic` | Constant `0x5742` (`'W''B'`) |
| 2 | 1 | `uint8` | `version` | Protocol version, must be `1` |
| 3 | 1 | `uint8` | `flags` | Bitfield (see §3) |
| 4 | 2 | `uint16` | `device_number` | PYNQ board ID |
| 6 | 2 | `uint16` | `wand_id` | Wand identifier (e.g. `1`, `2`) |
| 8 | 4 | `uint32` | `packet_number` | Monotonic sequence per device |
| 12 | 4 | `uint32` | `stroke_id` | Monotonic per wand/session |
| 16 | 2 | `int16` | `x_q` | X coordinate (Q15 normalized) |
| 18 | 2 | `int16` | `y_q` | Y coordinate (Q15 normalized) |
| 20 | 4 | `uint32` | `timestamp_ms` | Unix time (ms, low 32 bits) |

**Total:** 24 bytes

---

## 3. Flags Bitfield (`flags`)

| Bit | Mask | Name | Meaning |
|---:|:---:|------|---------|
| 0 | `0x01` | `PEN_DOWN` | 1 = drawing / contact |
| 1 | `0x02` | `STROKE_START` | First packet of a stroke |
| 2 | `0x04` | `STROKE_END` | Last packet of a stroke |
| 3 | `0x08` | Reserved | Must be 0 |
| 4–7 | — | Reserved | Must be 0 |

### MVP Rules
- A new stroke begins when `STROKE_START=1`.
- A stroke ends when `STROKE_END=1`.
- If `STROKE_END` is missing, Wand-Brain may close the stroke using timeout logic.

---

## 4. Coordinate Encoding

### Normalized Q15 Format (Recommended)

- `x_q`, `y_q` represent normalized coordinates in **[0, 1]**
- Encoding:

x_q = round(x_norm * 32767)
y_q = round(y_norm * 32767)

- Valid range: `0 … 32767`

This avoids floating-point transmission and is resolution-independent.

---

## 5. Stroke Semantics

- `stroke_id` is a **32-bit integer** incremented whenever a new stroke starts.
- Wand-Brain groups points by:
- (device_number, wand_id, stroke_id)
- PYNQ may determine stroke boundaries explicitly or rely on Wand-Brain timeout logic.

---

## 6. Packet Ordering & Loss

- UDP is lossy; **no retransmission** is required for MVP.
- `packet_number` must increase monotonically per `device_number`.
- Wand-Brain may:
- detect gaps
- mark strokes as lossy
- optionally interpolate

---

## 7. Validation Rules (Wand-Brain)

A packet is rejected if:
- `magic != 0x5742`
- `version != 1`
- packet length ≠ 24 bytes
- `x_q` or `y_q` outside `[0, 32767]` (for normalized mode)

---

## 8. Reference C Struct (Authoritative)

```c
#pragma pack(push, 1)
typedef struct {
  uint16_t magic;          // 0x5742 ("WB")
  uint8_t  version;        // 1
  uint8_t  flags;          // bitfield
  uint16_t device_number;  // PYNQ board ID
  uint16_t wand_id;        // Wand ID
  uint32_t packet_number;  // Monotonic sequence
  uint32_t stroke_id;      // Stroke identifier
  int16_t  x_q;            // Q15 normalized X
  int16_t  y_q;            // Q15 normalized Y
  uint32_t timestamp_ms;   // Unix time (ms, low 32 bits)
} wb_point_v1_t;
#pragma pack(pop)

```
# PYNQ Vision → Stroke Segmentation → UDP Packets (MVP Guide)

## Goal
From each IR camera frame, you extract `(x, y, t)` (blob centroid + timestamp).  
You must group consecutive valid points into **strokes** and send them as **wb-point-v1 UDP packets** to Wand-Brain (EC2).

---

## 1) Per-frame inputs you already have
For each camera frame:
- `t_ms` = PYNQ timestamp (ms)
- `blob_found` = boolean
- if `blob_found`: `x, y` (centroid) in pixels or normalized

(If available: `confidence` or `area` to reject noise.)

---

## 2) Define “valid point”
MVP:
- `valid = blob_found`
Better (if you have quality metrics):
- `valid = blob_found && confidence >= Cmin` (or `area >= Amin`)

Only **valid** frames produce UDP point packets.

---

## 3) Stroke definition (vision-only, no IMU needed)
A **stroke** is a contiguous run of valid points, separated by a short gap.

Use these defaults:
- `N_on = 2`  (need 2 consecutive valid frames to start a stroke)
- `N_off = 3` (need 3 consecutive invalid frames to end a stroke)
- `T_gap_end = 150 ms` (end stroke if no valid points for this long)

---

## 4) State machine
Maintain:
- `state ∈ {IDLE, ACTIVE}`
- `stroke_id` (uint32), starts at 0 and increments per new stroke
- `packet_number` (uint32), increments per sent UDP packet
- `last_valid_point = (x,y,t)` (for closing packet if needed)
- counters/timers: `valid_count`, `invalid_count`, `last_valid_time_ms`

### IDLE → ACTIVE (stroke start)
If `valid` for `N_on` consecutive frames:
- `stroke_id += 1`
- Next sent packet sets flags: `PEN_DOWN=1`, `STROKE_START=1`
- Enter ACTIVE

### ACTIVE (stroke continues)
For each frame:
- If `valid`:
  - send point packet with flags `PEN_DOWN=1`
  - update `last_valid_point`
  - reset invalid counters
- If `invalid`:
  - increment `invalid_count`
  - if `(t_ms - last_valid_time_ms) > T_gap_end` OR `invalid_count >= N_off`:
    - close stroke (see next section)
    - enter IDLE

---

## 5) Closing a stroke (important detail)
Problem: you only know the stroke ended *after* missing frames.

MVP solution:
- When ending, send **one extra UDP packet** using `last_valid_point` `(x,y,t_last)`
- Set flags: `PEN_DOWN=0`, `STROKE_END=1`
- Same `stroke_id`, new `packet_number`

This guarantees the backend sees a clean end marker.

---

## 6) UDP packet fields (wb-point-v1)
For every sent point packet:
- `device_number`: fixed per PYNQ board
- `wand_id`: 1 or 2 (competition)
- `packet_number`: increment each packet
- `stroke_id`: current stroke
- `timestamp_ms`: `t_ms` from PYNQ
- `x_q, y_q`: normalized Q15 preferred:
  - `x_q = round(x_norm * 32767)`
  - `y_q = round(y_norm * 32767)`

Flags:
- Middle of stroke: `PEN_DOWN=1`
- First packet: `PEN_DOWN=1 | STROKE_START=1`
- End packet: `STROKE_END=1` (and `PEN_DOWN=0`)

---

## 7) Output expectation
Wand-Brain will group points by:
`(device_number, wand_id, stroke_id)`  
and relies on `STROKE_START/STROKE_END` to segment reliably.

This protocol is vision-only for MVP (single clock, minimal complexity).