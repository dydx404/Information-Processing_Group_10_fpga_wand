# Templates, Scoring, And Target Selection APIs

This guide documents the Brain APIs responsible for template discovery, per-wand
target selection, and finalized-attempt scoring.

## Scope

The relevant implementation is split across:

- live scoring runtime:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- scoring functions:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py)
- cloud wrapper state:
  [`../../../cloud/main.py`](../../../cloud/main.py)

## Endpoint Map

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v2/templates` | list available template references |
| `GET` | `/api/v2/template/{template_id}/image.png` | serve one template image |
| `GET` | `/api/v2/wand/{wand_id}/target-template` | read the current target template for a wand |
| `PUT` | `/api/v2/wand/{wand_id}/target-template?template_id=...` | change a wand's selected template |
| `GET` | `/api/v2/score/latest?wand_id={id}&template_id={optional}` | score the latest finalized attempt for a wand |
| `GET` | `/api/v2/score/attempt/{attempt_id}?template_id={optional}` | score a specific finalized attempt |

## Template Discovery

### `GET /api/v2/templates`

This route lists the templates currently available in the template directory.

The response contains:

- `count`
- `templates[]`
  - `template_id`
  - `name`
  - `image_png`

The route uses `list_templates(...)` from
[`similarity.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py).

The template directory is the cloud-level template directory exposed through the
runtime:

- repo default source templates start in the backend package
- the wrapper ensures they are available in the cloud data directory

### `GET /api/v2/template/{template_id}/image.png`

This serves the PNG for a specific template.

If the `template_id` does not correspond to an existing PNG file, the route
returns `404`.

## Per-Wand Target Template Selection

Target-template selection is implemented by the wrapper layer in
[`software/cloud/main.py`](../../../cloud/main.py), not by the lower-level live
runtime alone.

### Internal State

Two internal maps are important:

- `selected_template_by_wand`
  the currently chosen target template for each wand
- `attempt_template_by_key`
  the template locked to a particular in-flight attempt, keyed by
  `(device_number, wand_id, attempt_id)`

This split lets the system distinguish:

- the operator's current template choice for the wand
- the template that should actually be used when scoring a specific attempt

### `GET /api/v2/wand/{wand_id}/target-template`

This returns the currently selected target template for the wand.

If no explicit template has been chosen yet, the service falls back to the
first available template and stores that choice for the wand.

The response includes:

- `wand_id`
- `template_id`
- `template_name`
- `image_png`
- `applies_to`

For a simple fetch, `applies_to` is reported as `"next_attempt"`.

### `PUT /api/v2/wand/{wand_id}/target-template?template_id=...`

This changes the wand's selected target template.

The interesting behavior is how the service decides whether that choice affects:

- the current active attempt, or
- only the next attempt

The wrapper checks whether:

- the wand currently has an active attempt
- that active attempt has not yet been associated with a template

If both are true, the new template is bound to the active attempt and the
response reports:

- `applies_to = "current_attempt"`

Otherwise the new template is stored as the wand's future default and the
response reports:

- `applies_to = "next_attempt"`

This is a useful detail in demonstrations because it explains why changing the
template mid-drawing may or may not affect the current stroke.

## Scoring APIs

Scoring applies only to finalized attempts, not live in-memory attempts.

### `GET /api/v2/score/latest?wand_id={id}&template_id={optional}`

This resolves the latest finalized attempt for the given wand and scores it.

If `template_id` is provided:

- only that one template is scored

If `template_id` is omitted:

- all known templates are scored
- the best candidate is chosen as `best`

### `GET /api/v2/score/attempt/{attempt_id}?template_id={optional}`

This scores a specific finalized attempt using the same scoring behavior as the
`latest` route.

This route is useful for database-backed or archival workflows where the caller
already knows the finalized `attempt_id`.

## Score Payload Structure

The scoring APIs return:

- `attempt_id`
- `source_stroke_id`
- `wand_id`
- `device_number`
- `num_points`
- `close_reason`
- `best`
  - `template_id`
  - `template_name`
  - `score`
  - `metrics`
- `all_candidates[]`
  - one scored candidate per template, sorted by score descending
- `attempt_image_png`

This payload is rich enough for:

- showing only the best score in the dashboard
- building a more detailed comparison view later
- debugging why one template beat another

## Scoring Algorithm

The scoring implementation lives in
[`similarity.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/scoring/similarity.py).

### Processing Steps

1. Open the attempt image and the template image.
2. Convert both to grayscale and resize to `256 x 256`.
3. Threshold them into binary masks.
4. Count:
   - pixels on in the drawing
   - pixels on in the template
   - intersection
   - union
5. Compute:
   - IoU
   - Dice coefficient
   - area ratio
6. Combine them into a weighted score out of `100`.

### Composite Score

The weighted score is:

- `55%` Dice
- `35%` IoU
- `10%` area ratio

So the service rewards:

- strong overlap with the template
- similar filled stroke area

The score result is rounded to three decimal places.

### Template Naming

Template display names are derived from the PNG filename stem by replacing
underscores and title-casing the result. That means the filename is the real
stable identifier, while the display name is a convenience label.

## Interaction With Persistence

The wrapper in `software/cloud/main.py` wraps the lower-level score payload
builder with `_persisting_score_attempt_payload(...)`.

That means a score lookup can also act as a persistence touchpoint:

- it reuses the runtime's score logic
- then attempts to upsert the scored attempt into the SQL database

Finalization-time persistence is still the main path, but this wrapper keeps the
score endpoints aligned with the stored attempt records.

## Frontend Consumption

The dashboard uses these APIs in two ways:

- template picker and preview via `/api/v2/templates`
- finalized score display via `/api/v2/score/latest`

The frontend typically:

1. fetches the latest finalized attempt
2. reads the locked `best_template_id`
3. calls `/api/v2/score/latest` with that template id
4. displays the score and selected metrics

This is why the score view updates only after a stroke is finalized.

## Operational Notes

- Templates are image-based, not vector-based.
- Scoring happens against rendered attempt PNGs, not raw point lists.
- Target-template selection is maintained in wrapper memory, not in the SQL
  database.
- The scoring endpoints depend on finalized attempt images being available on
  disk.
