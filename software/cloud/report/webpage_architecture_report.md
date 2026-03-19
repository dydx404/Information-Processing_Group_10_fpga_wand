# Wand Brain Webpage Architecture Report

## 1. Purpose

This report documents the design and behavior of the Wand Brain webpage served
by the backend.

The webpage is implemented as a single HTML file:

- [`../frontend/index.html`](../frontend/index.html)

and is served by:

- [`../main.py`](../main.py)

The page is intended to be both:

- an operator console during live use
- a presentation/demonstration dashboard for the project

## 2. Delivery Model

The webpage is served directly by the same FastAPI process that owns the live
runtime and database wrapper.

### 2.1 Routes

- `GET /`
  serves the main dashboard page
- `GET /frontend/*`
  serves additional static frontend assets if present

This means there is no separate frontend server and no separate SPA bundling
pipeline in the current architecture.

## 3. Frontend Technology Choice

The webpage is intentionally implemented as:

- plain HTML
- embedded CSS
- embedded JavaScript

It does not depend on:

- React
- Vue
- WebSockets
- a build system

This choice was suitable for the project because it kept the UI:

- easy to deploy
- easy to inspect
- easy to debug
- tightly aligned with the backend API contract

## 4. Visual Layout

The page is structured into three main vertical regions inside a grid:

### 4.1 Left Panel: Controls And Summaries

This panel contains:

- wand selector
- target template selector
- template application action
- manual refresh action
- node control form
- node-control summary cards
- live status summary text
- latest-attempt summary text

### 4.2 Center Panel: Live Visualization

This panel contains:

- the background template image
- the live drawing image
- live per-wand statistics such as:
  - mode
  - attempt id
  - point count
  - stroke timer
  - last point timestamp
  - close reason

### 4.3 Right Panel: Score, Leaderboards, And Database

This panel contains:

- latest score summary
- champion-claim panel
- template leaderboard table
- recent-attempt database table

The layout therefore mirrors the logical structure of the system:

- control on the left
- live drawing in the center
- history and ranking on the right

## 5. Styling And Presentation Language

The page defines its own visual system through CSS variables in `:root`.

Key properties of the current design:

- warm paper-like background colors
- serif headline/body styling
- soft bordered panels
- layered image frame for the live drawing
- compact table-based summaries for historical data

This gives the dashboard a deliberate presentation-friendly look while avoiding
the complexity of a design framework.

## 6. JavaScript Structure

The page script uses a small stateful client-side controller built with
functions and DOM references.

### 6.1 DOM Bindings

The script begins by binding all major UI elements with
`document.getElementById(...)`.

These bindings cover:

- status badges
- selectors and form inputs
- node-control buttons
- live-image elements
- live stat labels
- score section
- leaderboard table body
- database table body

This makes the page behave like a small manual UI controller rather than a
component framework.

### 6.2 Client-Side State Variables

The page maintains a small amount of runtime state:

- `selectedWand`
- `selectedDeviceNumber`
- `liveFrameAvailable`
- `inflightLive`
- `controlDraftDirty`
- `latestAttempt`
- `latestLeaderboards`
- `latestWandStatus`
- `latestWandStatusPerfMs`

These values allow the page to coordinate polling responses across sections and
derive a smoother user experience without over-fetching.

## 7. Frontend API Access Pattern

All JSON requests go through:

- `fetchJson(path, options = {})`

This helper:

- prefixes the backend origin
- performs the fetch
- checks `resp.ok`
- parses the JSON response

This makes the whole page a thin client over the backend APIs.

## 8. Polling Model

The webpage uses timed polling rather than server push.

### 8.1 Polling Intervals

The current intervals are:

| Function | Interval |
| --- | --- |
| `refreshHealth` | `4000 ms` |
| `refreshWands` | `1500 ms` |
| `refreshWandStatus` | `500 ms` |
| `refreshNodeControl` | `1200 ms` |
| `refreshLiveFrame` | `180 ms` |
| `renderTimerValue` | `120 ms` |
| `refreshLatestAttemptAndScore` | `1200 ms` |
| `refreshLeaderboards` | `2500 ms` |
| `refreshDatabase` | `5000 ms` |

### 8.2 Why The Intervals Differ

The polling cadence reflects the sensitivity of each UI surface:

- live image refresh is fast because it is the most visually dynamic element
- wand status is reasonably frequent to keep the timer and active state current
- database and leaderboard views are slower because they change only when
  attempts finalize
- health checks are slower still because they are coarse operational signals

This is a simple but effective way to balance responsiveness and request volume.

## 9. Main Webpage Functions

### 9.1 Health And Availability

`refreshHealth()` calls:

- `/api/v1/health`
- `/api/v1/database/health`

It updates:

- API status badge
- database status badge

This gives the operator immediate feedback on whether the core service and
persistence layer are available.

### 9.2 Template Discovery And Selection

`refreshTemplates()` calls:

- `/api/v2/templates`

`refreshTargetTemplate()` and `applyTargetTemplate()` call:

- `/api/v2/wand/{wand_id}/target-template`

These functions control:

- the template dropdown
- the background template image
- the status message describing whether the template applies to the current or
  next attempt

### 9.3 Wand Status And Live Session State

`refreshWands()` calls:

- `/api/v1/wands`

`refreshWandStatus()` calls:

- `/api/v1/wand/{wand_id}`

These functions populate:

- wand selector options
- active/idle summaries
- current attempt id
- current point count
- last close reason
- device number used for node control

### 9.4 Node Control Panel

`refreshNodeControl()` calls:

- `/api/v3/node/{device_number}/status`

`putNodeControl()` and the related action helpers call:

- `/api/v3/node/{device_number}/control`

The control panel supports:

- changing persistent control settings
- pausing or resuming transmission immediately
- clearing the local sketch
- triggering recalibration

The page formats both:

- the server-side desired control object
- the node-side acknowledgement object

This is important because it exposes queued vs applied control state clearly to
the operator.

### 9.5 Live Drawing View

`refreshLiveFrame()` fetches:

- `/api/v1/wand/{wand_id}/live.png`

The page uses two stacked images:

- `templateBg`
  reference template
- `liveDraw`
  live or finalized drawing image

The page also guards against overlapping image requests with `inflightLive`,
which reduces redundant refreshes.

### 9.6 Finalized Attempt And Score View

`refreshLatestAttemptAndScore()` calls:

- `/api/v1/attempt/latest?wand_id=...`
- `/api/v2/score/latest?wand_id=...&template_id=...`

This function is responsible for:

- switching from live view to finalized-attempt image when appropriate
- updating the latest attempt summary
- updating the score box
- exposing the current best metrics such as Dice and IoU

### 9.7 Leaderboard View

`refreshLeaderboards()` calls:

- `/api/v3/leaderboards`

It renders the champion table and also feeds the claim-panel logic.

### 9.8 Champion Name Claiming

`claimChampionName()` calls:

- `/api/v3/leaderboards/claim`

This lets the operator enter a player name for a newly achieved top score.

### 9.9 Database History View

`refreshDatabase()` calls:

- `/api/v1/database/attempts?limit=15`

It renders the recent-attempt table, including:

- database row id
- attempt id
- wand id
- duration
- point count
- score
- image link

## 10. Webpage Timing Model

The page treats live and finalized state differently.

### 10.1 While A Wand Is Active

When the selected wand is active:

- the center image is refreshed primarily from `live.png`
- the score panel shows a "drawing…" state
- the timer is updated continuously in the browser between polls

### 10.2 After Finalization

When the stroke is finalized:

- `attempt/latest` becomes authoritative
- the score endpoint becomes meaningful
- the recent-attempt table and leaderboards may update

This is a clean UI reflection of the backend architecture:

- live state first
- finalized history second

## 11. Timer Design

The page uses `renderTimerValue()` to make the stroke timer feel smoother than
raw polling alone would allow.

It combines:

- the last server-reported `current_duration_ms`
- a bounded `performance.now()` delta since the last status poll

This gives the appearance of a smoothly running timer while still anchoring the
actual timing to backend data.

## 12. Error Handling Strategy

The page generally handles each panel independently.

For example:

- if wand status fails, the live status area degrades without crashing the
  whole page
- if database queries fail, only the recent-attempt table shows an error
- if node control fails, the control summary and ack summary show error text

This design choice is valuable in a demo environment because partial backend
issues remain visible instead of collapsing the whole dashboard.

## 13. Caching Strategy

The page avoids stale images by:

- appending `?t=${Date.now()}` to image URLs
- relying on backend no-store headers for PNG routes

This is especially important for:

- `live.png`
- template background refreshes
- finalized attempt images

## 14. Why This Webpage Design Works Well

The current design works well for the project because it:

- exposes the whole system in one page
- stays close to the backend contract
- avoids frontend build/deployment complexity
- supports operator actions and debugging at the same time
- maps naturally onto the live/finalized/persistent split in the backend

## 15. Limitations

- The page is a hand-written controller rather than a component system, so it
  can become harder to maintain as features grow.
- Polling generates repeated requests even when values do not change.
- The page assumes a fairly small scale of concurrent wands and operators.

These limitations are acceptable for the project and consistent with the
overall architecture.
