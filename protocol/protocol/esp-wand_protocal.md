# ESP32 Wand Control (MVP v1) — User Story + Control Logic
**Scope:** ESP32 handles **button → IR LED + haptic** and sends **START/END events** to PYNQ.  
**IMU:** Ignored for MVP (single-go configuration, no runtime use).  
**Segmentation model:** One **attempt** per button-hold (press → release). PYNQ collects `(x,y,t)` only during an active attempt.

---

## 1) User Story (what the user experiences)

1. User holds the wand and **presses & holds** the button to begin.
2. Immediately on press:
   - IR LED turns **ON** (tracking enabled).
   - Wand signals PYNQ: **START** (new attempt begins).
3. After **3 seconds** of continuous holding:
   - Motor **vibrates once** to indicate “ready / start drawing now”.
4. User draws while continuing to hold the button.
5. When finished, user **releases** the button:
   - Motor **vibrates once** to confirm end.
   - IR LED turns **OFF**.
   - Wand signals PYNQ: **END** (attempt ends; PYNQ/brain can finalize scoring).

Notes:
- If the user releases before 3 seconds, the “ready” vibration does not happen, but END still happens normally.

---

## 2) Interface: ESP32 → PYNQ Event Signaling

ESP32 sends **events only** (not continuous streams).

### Required events
- `START`: button press accepted (debounced)
- `END`: button release accepted (debounced)

### Optional event (recommended for UX, not required by backend)
- `READY`: emitted at press + 3s (when the motor vibrates)

### Transport
- UART or UDP (team choice). Content below is transport-agnostic.

### Message content (minimum fields)
- `proto`: fixed version tag
- `seq`: monotonic uint32 sequence number
- `event`: `START` / `READY` / `END`
- `attempt_id`: monotonic uint32 (increments per press)
- `ts_ms`: ESP32 local ms since boot (for logging/debug only)

**Example (ASCII line format, easiest to debug):**
- `EVT,proto=wand-evt@1,seq=10,event=START,attempt=57,ts=123456\n`
- `EVT,proto=wand-evt@1,seq=11,event=READY,attempt=57,ts=126456\n`
- `EVT,proto=wand-evt@1,seq=12,event=END,attempt=57,ts=130012\n`

PYNQ behavior:
- On `START(attempt_id)`: begin accepting blob points into this attempt.
- On `END(attempt_id)`: stop accepting; flush/close attempt; backend can score.

---

## 3) Control Logic (Authoritative State Machine)

### Outputs
- `LED_IR`: ON/OFF
- `MOTOR`: vibrate pulse

### Inputs
- `BTN`: button pressed/released (debounced)

### Timing constants (defaults)
- `T_READY_MS = 3000` (press-and-hold time before READY vibration)
- `VIB_READY_MS = 120` (vibration pulse duration at READY)
- `VIB_END_MS = 120` (vibration pulse duration at END)
- `DEBOUNCE_MS = 30` (button debounce time)

### States
- `IDLE`: button not pressed, LED off
- `HOLDING`: button pressed, LED on, waiting for READY
- `ACTIVE`: READY already issued, still holding

### Transitions

#### IDLE → HOLDING (debounced press)
Actions (immediate):
- `attempt_id += 1`
- `seq += 1; send_event(START, attempt_id)`
- `LED_IR = ON`
- record `t_press_ms = now_ms()`
- set `ready_sent = false`

#### HOLDING → ACTIVE (if still pressed and now_ms() - t_press_ms ≥ T_READY_MS)
Actions:
- `pulse_motor(VIB_READY_MS)`
- (optional) `seq += 1; send_event(READY, attempt_id)`
- set `ready_sent = true`

#### HOLDING → IDLE (debounced release before READY time)
Actions:
- `pulse_motor(VIB_END_MS)`
- `LED_IR = OFF`
- `seq += 1; send_event(END, attempt_id)`
- reset internal counters

#### ACTIVE → IDLE (debounced release)
Actions:
- `pulse_motor(VIB_END_MS)`
- `LED_IR = OFF`
- `seq += 1; send_event(END, attempt_id)`
- reset internal counters

---

## 4) Requirements / Guarantees

### Guarantees ESP32 provides to PYNQ
- Exactly **one START** per attempt.
- Exactly **one END** per attempt.
- `attempt_id` is strictly increasing.
- `seq` is strictly increasing (detect drops/duplicates).
- LED is ON for the entire time between START and END (minus hardware propagation delays).

### Debounce requirement
- ESP32 must debounce button to avoid multiple START/END events from contact bounce.

### Failure handling (MVP)
- If communication fails, LED/motor behavior remains correct; PYNQ may miss events (acceptable for MVP, but log it).

---

## 5) Integration Notes (for the PYNQ team)
- Treat `attempt_id` as the grouping key for all `(x,y,t)` samples during the button-hold.
- Ignore ESP32 timestamps for fusion; use PYNQ local time for camera frames.
- If READY is implemented: it is a UX marker, not required for scoring.

---