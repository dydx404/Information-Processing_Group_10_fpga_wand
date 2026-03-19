# Live Runtime And Plotting APIs

This guide documents the live runtime APIs that let the dashboard monitor a
wand, fetch live and finalized drawings, and understand the current attempt
state.

## Scope

These routes are primarily implemented in:

- [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/render/rasterize.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/render/rasterize.py)
- [`../../../cloud/frontend/index.html`](../../../cloud/frontend/index.html)

They are the API surface behind the Brain dashboard's live plotting behavior.

## Endpoint Map

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | service health and live idle-finalize configuration |
| `GET` | `/api/v1/wands` | system-wide wand status snapshot |
| `GET` | `/api/v1/wand/{wand_id}` | detailed status for one wand |
| `GET` | `/api/v1/wand/{wand_id}/live.png` | current live drawing image |
| `GET` | `/api/v1/attempt/latest?wand_id={id}` | latest finalized attempt for a wand |
| `GET` | `/api/v1/attempt/{attempt_id}/image.png` | finalized attempt image |

There are also two development-oriented routes in the base runtime:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | minimal dev health check |
| `GET` | `/v1/debug/state` | internal in-memory state snapshot |

The dashboard and the final demo primarily rely on the `/api/v1/*` routes.

## Internal State Behind These APIs

The live runtime keeps the current drawing state in memory inside the
`BrainState` object in
[`server.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py).

The most important internal structures are:

- `attempts`
  active in-memory point buffers keyed by `(device_number, wand_id, attempt_id)`
- `last_result`
  latest finalized attempt per `(device_number, wand_id)`
- `attempt_index`
  finalized-attempt lookup by `attempt_id`
- `wand_status`
  live status object per `wand_id`
- `live_render_path`
  current PNG path served by `/api/v1/wand/{wand_id}/live.png`

This means the live plotting APIs are reporting on in-memory state first, not
the SQL database.

## Health API

### `GET /api/v1/health`

This route confirms that the Brain process is alive and returns some runtime
configuration:

- `ok`
- `service`
- `version`
- `time_ms`
- `idle_finalize_ms`

`idle_finalize_ms` is especially useful operationally because it tells you how
long the runtime waits before closing a still-active attempt due to inactivity.

## Wand Status APIs

### `GET /api/v1/wands`

This returns the current status of all known wands.

The payload is built from `wand_status` and includes:

- `wand_id`
- `active`
- `current_attempt_id`
- `last_point_ms`
- `device_number`
- `current_source_stroke_id`
- `current_start_ms`
- `current_points`
- `last_finalized_attempt_id`
- `last_close_reason`
- `last_stroke_duration_ms`
- `current_duration_ms`

`current_duration_ms` is calculated dynamically from:

- the current attempt start time
- the timestamp of the last received point

This route is the top-level status feed used by the frontend's wand list.

### `GET /api/v1/wand/{wand_id}`

This returns the same status model, but only for one wand.

If the wand is unknown, the route returns `404`.

This route is the main detailed status endpoint used by the live dashboard
panel. The frontend polls it frequently so it can show:

- whether the wand is actively drawing
- the current attempt id
- how many points are currently buffered
- the current timer value
- the last close reason when idle

## Live Plotting API

### `GET /api/v1/wand/{wand_id}/live.png`

This is the core live plotting endpoint.

It serves a PNG image representing the current in-memory stroke buffer for the
selected wand. The image is updated by the backend as points arrive.

### How The Live PNG Is Generated

Whenever a point is appended to an active attempt buffer, the runtime calls
`_render_live_if_due(...)`.

That function:

1. checks whether enough time has passed since the previous live render
2. calls `rasterize(...)`
3. writes the image to `data/outputs/wand_{wand_id}_live.png`
4. updates `live_render_path[wand_id]`

The renderer is implemented in
[`rasterize.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/render/rasterize.py).

For live plotting, it is called with:

- `size=256`
- `stroke=3`
- `normalize_view=False`

That last setting is a deliberate design choice. It means the renderer maps the
normalized protocol coordinates directly into a fixed canvas instead of zooming
to fit the current point cloud. As a result:

- the live drawing remains spatially stable over time
- the image does not jump or reframe while the user is still drawing

### Fallback Behavior

If there is no live render currently available, the route falls back to the
most recent finalized attempt image for that wand. If there is neither a live
image nor a finalized attempt, it returns `404`.

### Cache Behavior

The image response is served with no-store cache headers. The frontend also adds
a timestamp query parameter such as `?t=...` to ensure the browser fetches the
freshest frame.

## Finalized Attempt APIs

### `GET /api/v1/attempt/latest?wand_id={id}`

This returns the latest finalized attempt for a given wand.

The response contains:

- `attempt_id`
- `source_stroke_id`
- `wand_id`
- `device_number`
- `start_ms`
- `end_ms`
- `duration_ms`
- `num_points`
- `result`
  - `status`
  - `close_reason`
  - `best_template_id`
  - `best_template_name`
  - `score`
- `image_png`

Important semantics:

- `attempt_id` is the backend-owned internal attempt identifier
- `source_stroke_id` is the original UDP-side stroke id

The backend intentionally separates those two identifiers to avoid collisions
across restarts or reused sender-side ids.

### `GET /api/v1/attempt/{attempt_id}/image.png`

This serves the PNG image for a finalized attempt.

The image path is stored in the finalized result record and looked up through
`attempt_index`.

Like the live PNG route, this route returns a no-store image response.

## How Plotting Really Works Internally

The Brain service never receives image frames over the network. It reconstructs
drawings from point packets.

The plotting pipeline is:

1. UDP points are parsed into `PointEvent` objects.
2. Each point is appended to the active attempt buffer.
3. The live buffer is periodically rasterized into a PNG.
4. When the stroke ends, the final point list is rasterized again as the final
   attempt image.

The renderer itself is intentionally simple:

- one point becomes a small filled circle
- multiple points become a polyline

That simplicity is what makes the live plotting path reliable and easy to
inspect.

## Frontend Consumption

The dashboard in
[`software/cloud/frontend/index.html`](../../../cloud/frontend/index.html)
polls these routes on different intervals:

- `refreshWands` every `1500 ms`
- `refreshWandStatus` every `500 ms`
- `refreshLiveFrame` every `180 ms`
- `refreshLatestAttemptAndScore` every `1200 ms`

That means the website is not a push/WebSocket interface. It is an HTTP polling
dashboard over the live runtime APIs.

This choice has a few benefits for the project:

- easier debugging with a browser or `curl`
- no browser-side realtime connection complexity
- clear separation between live data ingress and dashboard refresh logic

## Operational Notes

- Live attempt state is in memory only.
- If the Brain process restarts, active live plots disappear.
- Finalized attempts can still be served afterward because they are saved as
  image files and may also be persisted to the SQL database by the wrapper
  layer.
- The plotting APIs do not themselves score drawings; they expose the live and
  finalized render products that later scoring APIs can evaluate.
