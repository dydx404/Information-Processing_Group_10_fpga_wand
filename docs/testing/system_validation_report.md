# System Validation Report

## 1. Purpose

This report documents what was actually validated on the integrated FPGA Wand
system, what issues were discovered during integration, what fixes were applied,
and what residual limitations remain.

It complements the procedural checklist in
[`test-plan.md`](./test-plan.md). The test plan describes how to run checks. The
current report describes the observed validation outcomes for the project as it
was integrated.

## 2. System Under Validation

The validated system consisted of the following main parts:

- PYNQ node runtime:
  [`../../FPGA/runtime/pynq_wand_brain_demo.py`](../../FPGA/runtime/pynq_wand_brain_demo.py)
- PYNQ UDP and HTTP bridge:
  [`../../FPGA/runtime/pynq_udp_bridge.py`](../../FPGA/runtime/pynq_udp_bridge.py)
- used FPGA design:
  [`../../FPGA/designs/centroid_pipeline/used_version/docs/design_summary.md`](../../FPGA/designs/centroid_pipeline/used_version/docs/design_summary.md)
- cloud wrapper:
  [`../../software/cloud/main.py`](../../software/cloud/main.py)
- live Brain runtime:
  [`../../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- frontend:
  [`../../software/cloud/frontend/index.html`](../../software/cloud/frontend/index.html)
- persistence layer:
  [`../../software/cloud/database/models.py`](../../software/cloud/database/models.py)

The validated architecture is also summarized in:

- [`../architecture/overview.md`](../architecture/overview.md)
- [`../../FPGA/runtime/ps_pl_flow.md`](../../FPGA/runtime/ps_pl_flow.md)
- [`../../software/protocol/protocol/pynq-udp-flow.md`](../../software/protocol/protocol/pynq-udp-flow.md)

## 3. Validation Strategy

Validation was performed in two complementary ways:

### 3.1 Tool-Based Validation

The repository contains synthetic and smoke-test tools used to validate the
cloud path independently of the physical board:

- [`../../software/tools/wb_connection_check.py`](../../software/tools/wb_connection_check.py)
- [`../../software/tools/full_system_smoke_test.py`](../../software/tools/full_system_smoke_test.py)

These tools were used to confirm:

- HTTP health endpoint reachability
- UDP packet acceptance
- parser and state-machine behavior
- finalized attempt creation
- image endpoint availability

### 3.2 Live Integration Validation

The most important validation happened on the integrated live system:

- real PYNQ board runtime
- real camera input
- actual FPGA centroid pipeline
- EC2-hosted Wand Brain service
- browser dashboard
- one-wand and two-wand user testing

This second category is the most significant because it validates the full
interaction between hardware, embedded runtime, network transport, backend
logic, persistence, and the operator-facing webpage.

## 4. Validation Environment

### 4.1 Board-Side

The board-side runtime validated:

- camera capture through OpenCV on PYNQ
- frame preprocessing and thresholding
- DMA transfer into the custom centroid IP
- MMIO register readback from the PL
- local sketch rendering
- UDP point transmission
- HTTP control polling and acknowledgement

### 4.2 Cloud-Side

The cloud service validated:

- UDP ingestion on port `41000`
- live HTTP service on port `8000`
- template scoring
- finalized attempt persistence
- node-control serving
- leaderboard and champion-name behavior

### 4.3 Frontend-Side

The webpage validated:

- live polling of wand status
- live image updates
- node-control form behavior
- score display
- recent attempts table
- leaderboard and claim flow
- stroke timer display

## 5. Validation Results Summary

The final integrated system achieved the following major outcomes:

| Area | Outcome |
| --- | --- |
| Cloud service startup | validated |
| UDP receive and parse | validated |
| Live plotting | validated |
| Finalized attempt rendering | validated |
| Template selection and scoring | validated |
| Database persistence | validated |
| Recent-attempt history | validated |
| Node control API and HTML panel | validated |
| Leaderboard promotion and name claim | validated |
| Stroke timer | validated |
| Single-wand end-to-end operation | validated |
| Two-wand concurrent operation | validated |

The most important project milestone was successful two-wand operation on the
same backend.

## 6. Detailed Validation Areas

## 6.1 Cloud Service Bring-Up

The cloud service was validated to:

- start successfully from the repository launcher
- serve the dashboard root page
- expose `/api/v1/health`
- listen on `8000/tcp` and `41000/udp`

This was tested both locally and on the live EC2 deployment.

### Result

Validated.

### Notes

During operation, the EC2 public IP changed at least once. The backend itself
remained functional once restarted and once the board-side `BRAIN_HOST`
configuration was updated.

## 6.2 UDP Transmission And Parser Validation

The UDP path was validated at three levels:

1. sender-side packet formation on PYNQ
2. raw socket receive on the cloud service
3. parser acceptance and conversion into live attempt state

The synthetic connectivity and smoke-test tools confirmed that:

- a generated `wb-point-v1` stroke reached the service
- the latest attempt reflected the expected `source_stroke_id`
- attempt images were generated and accessible through the HTTP image routes

### Result

Validated.

### Important Finding

The project converged on the correct semantic distinction between:

- UDP `stroke_id`
- backend-owned `attempt_id`

This prevented collisions when senders restarted or reused source stroke ids.

## 6.3 Board-Side Camera And PS/PL Pipeline

The live board validation covered:

- overlay loading
- DMA buffer allocation
- camera opening
- thresholded frame preprocessing
- custom IP MMIO stats readout
- centroid extraction
- local sketch generation

### Result

Validated, with caveats.

### Important Finding

Camera bring-up on PYNQ was not always reliable on first open. The final runtime
improved this by:

- trying more than one OpenCV backend
- performing camera warm-up reads
- failing more explicitly when no frames arrived

### Residual Caveat

The camera path can still require a restart in practice if the device state is
bad before runtime launch.

## 6.4 Live Plotting On The Dashboard

The backend and webpage were validated to show:

- template background
- live stroke updates during drawing
- finalized-attempt image after stroke completion

The live plotting path was confirmed to operate from real UDP point streams, not
from uploaded image frames.

### Result

Validated.

### Important Finding

The fixed-view live renderer was a good choice because the drawing remained
stable on screen while the stroke was still in progress.

## 6.5 Template Selection And Scoring

The template path was validated for:

- template list retrieval
- per-wand target-template selection
- finalized-attempt scoring
- score display on the webpage

Additional templates were added and served successfully, including:

- golden curve
- clover
- star

### Result

Validated.

### Important Finding

Template locking was correctly separated between:

- current active attempt, when appropriate
- next attempt, when a new selection arrived too late

That avoided ambiguity during live use.

## 6.6 Database Persistence

The database layer was validated for:

- creation and initialization
- finalized attempt storage
- recent-attempt retrieval
- champion row maintenance

The dashboard’s recent-attempt table and leaderboard view both depended on this
layer and were observed working against the live backend.

### Result

Validated.

### Important Finding

The recent-attempt view required correct ordering by finalization time rather
than only row creation time, especially when attempt rows were updated rather
than inserted.

## 6.7 Node Control Plane

The node-control system was validated in two ways:

- manual API testing against `/api/v3/node/...`
- frontend control-panel testing through the HTML interface

Validated behaviors included:

- fetching current control state
- updating control revisions
- node acknowledgement updates
- immediate pause/resume of transmission
- queued control changes for next stroke
- recalibrate and clear-sketch command dispatch

### Result

Validated.

### Important Finding

The control plane became substantially more usable once it was exposed in the
HTML dashboard rather than only through manual API calls.

## 6.8 Leaderboards And Champion Claiming

The leaderboard functionality was validated for:

- selecting the top score per template
- showing the champion table on the webpage
- allowing the current top-scoring attempt to claim a player name
- rejecting claim attempts for non-champion attempts

### Result

Validated.

### Important Finding

The correct behavior is not "any score can leave a name". Only the current top
attempt for that template can claim the champion slot.

## 6.9 Stroke Timer

The standalone timer functionality was validated in two modes:

- active stroke timing on the live page
- finalized duration display in recent attempts and latest attempt summaries

### Result

Validated.

### Important Finding

The timer worked without changing the board-side UDP format because the backend
already had enough timing information from the transmitted timestamps.

## 6.10 Single-Wand End-To-End Operation

The system was validated end to end with one active wand:

- drawing visible on the dashboard
- finalized attempt generated
- score computed
- recent-attempt history updated
- timer updated
- control path remained functional

### Result

Validated.

This was the first major integrated success condition.

## 6.11 Two-Wand Concurrent Operation

The system was then validated with two independent wands using the same backend.

The final integrated outcome was successful two-wand operation, including:

- both wands transmitting to the same backend
- the backend separating them correctly by `device_number` and `wand_id`
- live drawing and finalized attempt handling remaining functional

### Result

Validated.

### Significance

This was a major integration milestone because it demonstrated that the system
was no longer just working in a single isolated test path. It was functioning
as a multi-node interactive system.

## 7. Main Issues Found During Integration

The following issues were discovered during live integration.

## 7.1 Camera Bring-Up Instability

Observed behavior:

- camera sometimes failed to open cleanly
- startup could appear stuck at the camera step

Mitigation applied:

- more robust camera opening logic
- warm-up reads
- fallback backend attempts

## 7.2 Noisy Centroid Behavior

Observed behavior:

- unstable point vs line rendering
- tiny false starts
- occasional centroid noise

Mitigation applied:

- stronger runtime filtering and smoothing logic
- sketch-side jump rejection
- longer stroke hold behavior
- duplicate-hardware-result suppression via `frame_id`

## 7.3 Backend Attempt Identity Problems

Observed behavior:

- reused source stroke ids could collide with backend persistence
- oversized attempt-id behavior caused database issues

Mitigation applied:

- backend-owned internal `attempt_id`
- preservation of UDP `stroke_id` only as `source_stroke_id`

## 7.4 Idle Finalization Mismatch

Observed behavior:

- mismatch between board-side stroke hold timing and backend idle finalization
- possible fragmentation into tiny attempts

Mitigation applied:

- backend idle-finalize window tuning
- sender-side explicit stroke end behavior

## 7.5 Missing HTML Control Surface

Observed behavior:

- node control initially required manual API calls

Mitigation applied:

- addition of a dedicated HTML node-control panel

## 8. Residual Limitations

The final validated system still has important limitations:

- the PL centroid logic is still single-blob based rather than full
  segmentation
- active live state is not durable across backend restarts
- the webpage uses polling rather than push updates
- camera bring-up on embedded Linux is still not perfectly deterministic
- the board-side behavior depends on correct EC2 public IP configuration
- node control only affects boards running the updated control-aware runtime

These limitations do not invalidate the integrated success of the system, but
they are important to state explicitly.

## 9. Overall Assessment

The project successfully validated the complete intended interaction chain:

- camera input on PYNQ
- FPGA-assisted centroid extraction
- PS-side filtering and stroke generation
- UDP packet transport
- cloud-side receive, parse, render, and score
- persistence and leaderboard updates
- webpage monitoring and control
- successful operation with two concurrent wands

From a system-integration perspective, this is a strong result. The most
important claim that can be defended is:

The project did not only produce isolated components. It produced a working
multi-part interactive system that was validated live end to end.
