# Node Control APIs

This guide documents the HTTP control plane used by the Brain service to
influence PYNQ runtime behavior.

## Scope

The relevant implementation is split between:

- control-store implementation:
  [`../../../cloud/node_control.py`](../../../cloud/node_control.py)
- wrapper routes:
  [`../../../cloud/main.py`](../../../cloud/main.py)
- board-side consumer:
  [`../../../FPGA/runtime/pynq_wand_brain_demo.py`](../../../FPGA/runtime/pynq_wand_brain_demo.py)
- board-side HTTP client:
  [`../../../FPGA/runtime/pynq_udp_bridge.py`](../../../FPGA/runtime/pynq_udp_bridge.py)

The node-control APIs are intentionally separate from the UDP point stream.

## Endpoint Map

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v3/node-controls` | list all known node control and ack records |
| `GET` | `/api/v3/node/{device_number}/control` | fetch the control object for one node |
| `PUT` | `/api/v3/node/{device_number}/control` | update the control object for one node |
| `GET` | `/api/v3/node/{device_number}/status` | fetch control and ack together |
| `POST` | `/api/v3/node/{device_number}/ack` | record what the node has actually applied |

## Why HTTP Is Used Here

The project deliberately separates:

- UDP for low-latency point ingestion
- HTTP for readable, versioned, debuggable control

That makes the control plane easier to:

- inspect with a browser or `curl`
- version with revisions
- persist on disk
- evolve without touching the UDP packet format

## Control Store Model

The control state is managed by `NodeControlStore` in
[`node_control.py`](../../../cloud/node_control.py).

It stores two related objects per device:

- `control`
  what the server wants the node to do
- `ack`
  what the node reports it has actually applied

These are persisted in:

- `software/cloud/data/node_control_state.json`

This is operational state, not historical leaderboard data, so it is stored in
JSON rather than the SQL database.

## Default Control Object

The default control object contains:

- `device_number`
- `revision`
- `enabled`
- `armed`
- `tx_enabled`
- `mode`
- `apply_on`
- `vision`
  - `threshold`
  - `min_count`
- `stroke`
  - `gap_timeout_ms`
  - `max_jump`
  - `smoothing_alpha`
- `commands`
  - `clear_sketch_token`
  - `recalibrate_token`
- `updated_at_ms`

This schema mirrors the runtime knobs actually consumed by the PYNQ loop.

## Ack Object

The default ack object contains:

- `device_number`
- `applied_revision`
- `active_stroke`
- `tx_active`
- `mode`
- `pending_revision`
- `last_error`
- `command_tokens`
  - `clear_sketch_token`
  - `recalibrate_token`
- `last_seen_ms`

This lets the dashboard distinguish:

- what the server asked for
- what the node is actually doing right now

## `GET /api/v3/node-controls`

This returns a list of all known node records, each containing:

- `control`
- `ack`

It is useful for operator dashboards and multi-board monitoring.

## `GET /api/v3/node/{device_number}/control`

This returns the control-plus-ack payload for one node:

- `ok`
- `device_number`
- `control`
- `ack`

It is the main fetch route used by the board to read its current configuration.

## `PUT /api/v3/node/{device_number}/control`

This is the main update route for server-driven control changes.

### Supported Top-Level Fields

- `enabled`
- `armed`
- `tx_enabled`
- `mode`
- `apply_on`
- `vision`
- `stroke`
- `commands`

### Validation And Clamping

The control store validates and clamps several values:

- `mode` must be one of:
  - `normal`
  - `precision`
  - `fast`
  - `noisy_room`
- `apply_on` must be one of:
  - `immediate`
  - `next_attempt`
- `vision.threshold` is clamped to `0..255`
- `vision.min_count` is clamped to at least `1`
- `stroke.gap_timeout_ms` is clamped to at least `100`
- `stroke.max_jump` is clamped to at least `1`
- `stroke.smoothing_alpha` is clamped to `0.0..1.0`

### Revision Behavior

The store increments `revision` only when the effective control object actually
changes.

That is a very important semantic detail:

- repeated PUTs with the same values do not create fake new revisions
- the board can compare `incoming revision` vs `applied revision` cleanly

### Command Tokens

The `commands` object is token-based rather than boolean-state based.

When the caller sets:

- `clear_sketch: true`
- `recalibrate: true`

the store increments the corresponding token counters. This avoids ambiguity and
allows the board to detect one-shot commands reliably even if it polls later.

## `GET /api/v3/node/{device_number}/status`

This returns the same combined control-and-ack payload as the `control` fetch,
but is named for dashboard readability.

It is the route the frontend uses to show:

- current control state
- last node ack
- pending revision information

## `POST /api/v3/node/{device_number}/ack`

This route is how the PYNQ board reports what it has applied.

The board posts fields such as:

- `applied_revision`
- `active_stroke`
- `tx_active`
- `mode`
- `pending_revision`
- `last_error`
- `command_tokens`

The store updates `last_seen_ms` on every ack, which lets the UI decide whether
the node has polled recently.

## How The Board Uses The Control Plane

The PYNQ runtime uses the control plane in several stages.

### Initial Fetch

At startup, the board:

1. performs the Brain health check
2. fetches the initial control payload
3. applies it before entering the main loop

### Polling

Inside the main loop, the board polls control every
`CONTROL_POLL_INTERVAL_MS`.

When a new revision is seen, it either:

- applies it immediately, or
- queues it until no stroke is active

That decision is based on `apply_on`.

### Ack Feedback

The board posts acks:

- after applying a control revision
- periodically during normal operation
- during shutdown cleanup when possible

This gives the server and UI a partial closed loop rather than only one-way
control messages.

## Runtime Effects On The Board

The control plane influences real PS-side logic. It is not just display state.

The current runtime uses control values to affect:

- thresholding
- minimum blob count
- gap timeout
- stroke jump rejection
- smoothing level
- whether tracking is enabled
- whether new strokes are allowed
- whether UDP transmission is enabled

One-shot commands also trigger:

- sketch clearing
- threshold recalibration using live camera frames

For the detailed board-side behavior, see
[../../../FPGA/runtime/ps_pl_flow.md](../../../FPGA/runtime/ps_pl_flow.md).

## Operational Notes

- Control state survives service restarts because it is persisted to JSON.
- Ack freshness depends on the board continuing to poll.
- `status` and `control` are intentionally similar so both humans and boards can
  use them conveniently.
- The node-control APIs are designed to be safe for manual testing with `curl`
  or the HTML control panel.
