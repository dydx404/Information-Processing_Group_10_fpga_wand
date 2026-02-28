# Wand-Brain UDP Input Protocol (Revised)  
**PYNQ Board → Wand-Brain (EC2)**  
**Protocol name:** `wb-point-v1`  
**Status:** MVP / frozen for team coordination  
**Design note:** In MVP, we use **button-hold = one drawing attempt**. The field `stroke_id` is retained for compatibility but is defined as **attempt_id**.

---

## 1. Transport

- **Protocol:** UDP
- **Direction:** PYNQ → Wand-Brain
- **One UDP datagram = one point sample**
- **Endianness:** Little-endian
- **Recommended port:** `41000`
- **Packet size:** **24 bytes (fixed)**

This protocol is intentionally fixed-size and binary for low latency and easy parsing.

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
| 12 | 4 | `uint32` | `stroke_id` | **MVP meaning: attempt_id** (button press → release) |
| 16 | 2 | `int16` | `x_q` | X coordinate (Q15 normalized) |
| 18 | 2 | `int16` | `y_q` | Y coordinate (Q15 normalized) |
| 20 | 4 | `uint32` | `timestamp_ms` | PYNQ timestamp (ms, low 32 bits) |

**Total:** 24 bytes

---

## 3. Flags Bitfield (`flags`)

| Bit | Mask | Name | Meaning (MVP) |
|---:|:---:|------|----------------|
| 0 | `0x01` | `PEN_DOWN` | 1 = within active attempt (button held) |
| 1 | `0x02` | `STROKE_START` | First point packet of an attempt |
| 2 | `0x04` | `STROKE_END` | Final point packet of an attempt |
| 3 | `0x08` | Reserved | Must be 0 |
| 4–7 | — | Reserved | Must be 0 |

### MVP Rules
- `stroke_id` is treated as **attempt_id**.
- An attempt begins when PYNQ receives **START** from ESP32 (button press).
- An attempt ends when PYNQ receives **END** from ESP32 (button release).
- `STROKE_START=1` is set on the **first valid point** sent during the attempt.
- `STROKE_END=1` is set on the **final point** sent for the attempt (see §6.4).
- `PEN_DOWN=1` is set on all point packets sent while the attempt is active.

> Note: If an attempt contains **zero valid points** (no blob detected), no point packets are sent; Wand-Brain will not see that attempt via this protocol.

---

## 4. Coordinate Encoding

### Normalized Q15 Format (Required for MVP)

- `x_q`, `y_q` represent normalized coordinates in **[0, 1]**
- Encoding:
  - `x_q = round(x_norm * 32767)`
  - `y_q = round(y_norm * 32767)`
- Valid range: `0 … 32767`

This avoids floating-point transmission and is resolution-independent.

---

## 5. Attempt Semantics (MVP)

### Grouping key
Wand-Brain groups points by:
- `(device_number, wand_id, stroke_id)`  
where `stroke_id` **== attempt_id** for MVP.

### Lifecycle
- PYNQ opens an attempt on ESP32 `START`.
- PYNQ closes an attempt on ESP32 `END`.
- Wand-Brain should finalize processing for an attempt when it receives `STROKE_END=1`.

---

## 6. PYNQ Rules for Emitting Packets (MVP)

### 6.1 Per-frame inputs
From each IR camera frame PYNQ may obtain:
- `t_ms` (PYNQ timestamp, ms)
- blob detection result:
  - `blob_found` boolean
  - if found: `(x, y)` centroid (pixels or normalized)

### 6.2 Define “valid point”
MVP:
- `valid = blob_found`
Better (if available):
- `valid = blob_found && confidence >= Cmin` (or `area >= Amin`)

Only valid frames produce UDP point packets.

### 6.3 Packet emission during an active attempt
While attempt is active (button held):
- For each frame where `valid == true`:
  - send one `wb-point-v1` packet containing `(x_q, y_q, timestamp_ms)`
  - set `PEN_DOWN=1`
  - increment `packet_number` each sent packet

### 6.4 First/Last packet markers (START/END flags)
Because blob detection may not be valid exactly at the press/release moment, flags are applied to **point packets**, not button events.

- **First valid point in the attempt**:
  - set `STROKE_START=1` (and `PEN_DOWN=1`)
- **On attempt end (button released)**:
  - if at least one valid point was previously sent:
    - send **one final packet** using the `last_valid_point`
    - set `STROKE_END=1` and `PEN_DOWN=0`
    - keep same `stroke_id` (attempt_id), increment `packet_number`

This ensures Wand-Brain always receives a clean end marker when points exist.

---

## 7. Packet Ordering & Loss

- UDP is lossy; **no retransmission** is required for MVP.
- `packet_number` must increase monotonically per `device_number`.
- Wand-Brain may:
  - detect gaps using `packet_number`
  - mark attempts as lossy
  - optionally interpolate

---

## 8. Validation Rules (Wand-Brain)

A packet is rejected if:
- `magic != 0x5742`
- `version != 1`
- packet length ≠ 24 bytes
- `x_q` or `y_q` outside `[0, 32767]`

---

## 9. Reference C Struct (Authoritative)

```c
#pragma pack(push, 1)
typedef struct {
  uint16_t magic;          // 0x5742 ("WB")
  uint8_t  version;        // 1
  uint8_t  flags;          // bitfield
  uint16_t device_number;  // PYNQ board ID
  uint16_t wand_id;        // Wand ID (1..N)
  uint32_t packet_number;  // Monotonic sequence (per device)
  uint32_t stroke_id;      // MVP meaning: attempt_id (button hold)
  int16_t  x_q;            // Q15 normalized X in [0..32767]
  int16_t  y_q;            // Q15 normalized Y in [0..32767]
  uint32_t timestamp_ms;   // PYNQ timestamp (ms, low 32 bits)
} wb_point_v1_t;
#pragma pack(pop)