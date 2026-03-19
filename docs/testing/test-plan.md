# Test Plan

This document summarizes the practical validation strategy for the current
system.

## 1. Cloud Service Sanity Check

Start the cloud app:

```bash
cd software/cloud
bash start_script.sh --install-deps
```

Confirm:

- `GET /api/v1/health` returns `ok: true`
- `GET /api/v2/templates` returns the expected template list
- the dashboard loads on `http://127.0.0.1:8000/`

## 2. UDP Connectivity Check

Use the lightweight connection script:

```bash
python3 software/tools/wb_connection_check.py --host 127.0.0.1
```

Expected outcome:

- HTTP health succeeds
- one synthetic UDP stroke is accepted
- the latest attempt matches the transmitted `source_stroke_id`

## 3. End-to-End Smoke Test

Use the full-system smoke test:

```bash
python3 software/tools/full_system_smoke_test.py --host 127.0.0.1 --rates 25,50,100
```

Expected outcome:

- all configured strokes finalize
- live and finalized image endpoints return PNGs
- received-point counts are within the configured tolerance

## 4. PYNQ Board Validation

On each board, verify:

- camera opens reliably
- DMA/MMIO centroid reads update frame-to-frame
- the node can reach `BRAIN_HOST` over both HTTP and UDP
- control polling acknowledges revisions under `/api/v3/node/*`
- drawing appears under the correct `wand_id` and `device_number`

## 5. Frontend Validation

On the live console, verify:

- live image updates during a stroke
- recent attempts update after finalize
- template selection affects scoring target
- node-control buttons change node ack state
- leaderboard claim flow works only for the top score
- stroke timer updates during active drawing and finalizes correctly

## 6. Regression Focus Areas

Whenever the protocol or cloud state machine changes, re-check:

- `stroke_id` vs backend `attempt_id` handling
- idle finalization timing
- explicit `STROKE_END` handling
- multi-wand separation by `device_number` and `wand_id`
- database persistence after finalize
- leaderboard promotion and name-claim behavior
