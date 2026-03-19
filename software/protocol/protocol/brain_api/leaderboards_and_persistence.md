# Leaderboards And Persistence APIs

This guide documents the parts of the Brain service that persist finalized
attempts, expose historical data, and maintain the per-template leaderboard.

## Scope

The relevant implementation is split between:

- cloud wrapper and persistence hooks:
  [`../../../cloud/main.py`](../../../cloud/main.py)
- SQLAlchemy models:
  [`../../../cloud/database/models.py`](../../../cloud/database/models.py)
- base live runtime finalization:
  [`../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py`](../../../cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)

## Endpoint Map

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v3/leaderboards` | list current champions by template |
| `POST` | `/api/v3/leaderboards/claim` | assign a player name to a champion attempt |
| `GET` | `/api/v1/database/health` | report database availability |
| `GET` | `/api/v1/database/attempts?limit={n}` | list recent persisted attempts |

## Persistence Architecture

The Brain service makes a deliberate distinction between:

- live attempt state held in memory
- finalized historical data held in the SQL database

This means:

- while a stroke is still being drawn, it exists only in runtime memory
- once it is finalized, it may be written to the database and used for history
  and leaderboard features

This design keeps the hot ingest path lightweight while still preserving the
results that matter.

## Data Models

### `Attempt`

The `Attempt` table stores one finalized drawing result.

Its key fields are:

- `wand_id`
- `attempt_id`
- `device_number`
- `start_ms`
- `end_ms`
- `finalized_at_ms`
- `num_points`
- `render_path`
- `status`
- `best_template_id`
- `best_template_name`
- `score`
- `created_at`

This is the main historical record for a finalized drawing.

### `TemplateChampion`

The `TemplateChampion` table stores the current top result for each template.

Its key fields are:

- `template_id`
- `template_name`
- `attempt_id`
- `wand_id`
- `device_number`
- `finalized_at_ms`
- `score`
- `player_name`
- `claimed_at`
- `created_at`
- `updated_at`

The important semantic detail is that there is only one current champion row per
template.

## How Finalized Attempts Reach The Database

The wrapper layer in [`software/cloud/main.py`](../../../cloud/main.py) hooks
into the base runtime by replacing:

- `state._add_point_locked`
- `state._finalize_locked`
- `brain_server._score_attempt_payload`

### Finalization Hook

When the base runtime finalizes an attempt:

1. it produces a `FinalResult`
2. the wrapper looks up the selected template for that attempt
3. if a template is known, it computes a score
4. it calls `upsert_attempt_record(...)`
5. it may promote the attempt into `TemplateChampion`

This means persistence is not a separate batch process. It happens as part of
the finalized-attempt flow.

### Attempt Upsert Behavior

`upsert_attempt_record(...)` either:

- creates a new `Attempt` row, or
- updates an existing row with the same
  `(device_number, wand_id, attempt_id)`

That makes the persistence path resilient to repeated score updates or repeated
finalization-related writes.

## Leaderboard Promotion Rules

Champion promotion happens through `_maybe_promote_template_champion(...)`.

The promotion rules are:

- if the attempt has no scored template, it cannot become champion
- if the champion row already points at this same attempt, the row is refreshed
- if the existing champion has a score greater than or equal to the new score
  within a small epsilon, the champion remains unchanged
- otherwise the new attempt replaces the champion for that template

When a new champion is promoted:

- `attempt_id`, `wand_id`, `device_number`, `finalized_at_ms`, and `score` are
  updated
- `player_name` is cleared
- `claimed_at` is cleared

That means a new best score resets the champion-name claim until someone claims
the new top attempt.

## `GET /api/v3/leaderboards`

This route returns one leaderboard entry per available template.

The response contains:

- `count`
- `leaderboards[]`
  - `template_id`
  - `template_name`
  - `champion`

If no champion exists for a template yet, `champion` is `null`.

Otherwise the champion payload contains:

- `id`
- `template_id`
- `template_name`
- `attempt_id`
- `wand_id`
- `device_number`
- `finalized_at_ms`
- `score`
- `player_name`
- `claimed`
- `image_png`
- `claimed_at`
- `created_at`
- `updated_at`

This route is designed to drive both the leaderboard table and the champion-name
claim panel on the frontend.

## `POST /api/v3/leaderboards/claim`

This route lets the current champion for a template attach a player name to the
winning attempt.

### Required Inputs

- `attempt_id`
- `player_name`

### Validation

The route validates that:

- `attempt_id` is a positive integer
- `player_name` is non-empty after whitespace normalization
- `player_name` is at most `32` characters
- the given `attempt_id` is the current champion for some template

If the attempt is not the current champion, the route returns `404`.

### Success Behavior

On success, the route:

- updates `player_name`
- sets `claimed_at`
- returns the refreshed champion payload

This keeps the leaderboard write path very narrow and easy to reason about.

## `GET /api/v1/database/health`

This route reports whether the SQL database is currently available.

The response contains:

- `ok`
- `warning`

This is useful in environments where the live runtime may still be operating
even if persistence failed during startup.

## `GET /api/v1/database/attempts?limit={n}`

This route returns recent persisted attempts ordered by:

- `finalized_at_ms` descending
- then `id` descending

The route is intentionally history-oriented rather than live-oriented.

Each row payload contains:

- `id`
- `attempt_id`
- `wand_id`
- `device_number`
- `start_ms`
- `end_ms`
- `duration_ms`
- `finalized_at_ms`
- `num_points`
- `status`
- `best_template_id`
- `best_template_name`
- `score`
- `render_path`
- `image_png`
- `created_at`

This is the route behind the dashboard's "Recent Attempts" table.

## Relationship To Live APIs

The persistence and leaderboard APIs sit on top of the live runtime, but they
serve a different purpose.

Live APIs answer questions like:

- what is the wand doing now?
- what does the current sketch look like?

Persistence and leaderboard APIs answer questions like:

- what happened recently?
- what score was recorded?
- who currently holds the best score for a template?

That separation makes the service easier to reason about in both code and UI.

## Operational Notes

- The SQL database is not required for UDP ingestion itself.
- If the database is unavailable, live drawing can still work while persistence
  and leaderboard features degrade.
- Finalized attempt images are stored on disk and referenced by path in the
  database.
- Champion rows are derived from scored finalized attempts, not from live
  partial strokes.
