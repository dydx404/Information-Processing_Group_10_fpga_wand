# Wand Brain Database Architecture Report

## 1. Purpose

This report documents the database layer of the Wand Brain cloud backend. It
explains:

- how the database is configured
- what data is stored
- when data is written
- how the backend and webpage consume persisted records

The report is based on:

- [`../database/database.py`](../database/database.py)
- [`../database/models.py`](../database/models.py)
- [`../main.py`](../main.py)

## 2. Role Of The Database In The System

The SQL database is not the live ingest engine of the system.

Instead, it serves as the persistence layer for finalized, meaningful results.
Its main purposes are:

- storing finalized attempts
- storing current template champions
- enabling historical views in the webpage
- supporting leaderboard and champion-name features

This means the database is intentionally downstream of the real-time runtime,
not upstream of it.

## 3. Configuration And Engine Setup

Database configuration is defined in:

- [`../database/database.py`](../database/database.py)

### 3.1 Default Database Path

The default database is SQLite, stored at:

- [`../data/fpgawand.sqlite3`](../data/fpgawand.sqlite3)

The path is derived from the cloud directory and created automatically if
needed.

### 3.2 Environment Override

The backend supports overriding the database through:

- `DATABASE_URL`

If `DATABASE_URL` is not set, the service uses the default SQLite file.

### 3.3 SQLAlchemy Setup

The file creates:

- `engine`
- `SessionLocal`
- `Base`

When using SQLite, the engine adds:

- `check_same_thread = False`

This is appropriate for the current application because the service contains
background threads as well as request-handling paths.

## 4. Database Initialization

Database initialization happens in the wrapper layer:

- [`../main.py`](../main.py)

The key startup function is:

- `initialize_database()`

This function:

- calls `Base.metadata.create_all(bind=engine)`
- sets the runtime flags `DB_READY` and `_DB_WARNING`
- keeps startup resilient by catching initialization failures

This means the backend can still start even if persistence is unavailable,
which is useful in live demo environments.

## 5. Data Model

The database currently has two main tables:

- `Attempt`
- `TemplateChampion`

### 5.1 `Attempt`

The `Attempt` table stores finalized drawing attempts.

#### Core Identity Fields

- `id`
  database primary key
- `attempt_id`
  backend-owned finalized attempt identifier
- `wand_id`
  logical wand/player id
- `device_number`
  physical node/board id

#### Timing Fields

- `start_ms`
- `end_ms`
- `finalized_at_ms`
- `created_at`

These fields support both:

- gameplay/history views
- operational debugging

#### Content And Scoring Fields

- `num_points`
- `render_path`
- `status`
- `best_template_id`
- `best_template_name`
- `score`

These fields connect the finalized drawing to its visual artifact and scoring
result.

### 5.2 `TemplateChampion`

The `TemplateChampion` table stores the current top attempt for each template.

#### Identity And Ownership

- `id`
- `template_id`
- `template_name`
- `attempt_id`
- `wand_id`
- `device_number`

#### Ranking Fields

- `finalized_at_ms`
- `score`

#### Claiming Fields

- `player_name`
- `claimed_at`
- `created_at`
- `updated_at`

The unique constraint on `template_id` makes this table a "current champion per
template" table rather than a full historical ranking log.

## 6. What The Database Does Not Store

A key architectural decision is that the database does **not** store:

- raw UDP packets
- per-point live stroke buffers
- partially active attempts
- node-control operational state

Those remain in:

- runtime memory for live drawing state
- JSON for node-control state

This separation keeps the SQL schema focused on durable application results.

## 7. Finalize-Time Persistence Flow

The main persistence path is attached to attempt finalization.

### 7.1 Runtime Finalization

The base runtime finalizes attempts in:

- [`../backend/versions/brain_v2_scoring/src/brain/api/server.py`](../backend/versions/brain_v2_scoring/src/brain/api/server.py)

This produces a `FinalResult` containing:

- attempt identity
- point count
- timing
- render path
- close reason

### 7.2 Wrapper Hook

The wrapper replaces `state._finalize_locked` with its own
`_persisting_finalize_locked(...)`.

That wrapper:

1. calls the original finalize logic
2. determines the template associated with the attempt
3. computes a score if a template is available
4. calls `upsert_attempt_record(...)`
5. optionally promotes the attempt to champion

This is a powerful design because it lets the persistence layer stay outside the
core runtime while still integrating tightly with the finalization event.

## 8. Attempt Upsert Strategy

The function:

- `upsert_attempt_record(res, promote_champion=False)`

is the main persistence helper.

It searches for an existing `Attempt` row matching:

- `device_number`
- `wand_id`
- `attempt_id`

Then it either:

- inserts a new row, or
- updates the existing one

This protects the backend from duplicate persistence logic and allows repeated
score updates or retry-style writes without creating duplicate historical rows.

## 9. Template Champion Promotion

Champion promotion is handled by:

- `_maybe_promote_template_champion(...)`

The promotion rules are:

1. the attempt must have a valid `best_template_id`
2. the attempt must have a numeric `score`
3. if it is already the champion row, the row is refreshed
4. if its score is not better than the current champion, nothing changes
5. if its score is better, it becomes the new champion

When a new champion is promoted:

- the champion row is updated
- `player_name` is cleared
- `claimed_at` is cleared

This ensures that champion-name ownership always belongs to the current top
attempt only.

## 10. Champion Backfill On Startup

The wrapper includes:

- `backfill_template_champions()`

This scans stored `Attempt` rows and reconstructs the `TemplateChampion` table
if needed.

This is a useful recovery mechanism because it makes the leaderboard derivable
from historical finalized attempts rather than relying only on live updates at
the moment of scoring.

## 11. Database-Facing API Endpoints

The main persistence-oriented routes are:

- `GET /api/v1/database/health`
- `GET /api/v1/database/attempts`
- `GET /api/v3/leaderboards`
- `POST /api/v3/leaderboards/claim`

### 11.1 Database Health

`/api/v1/database/health` exposes:

- whether the database is available
- any warning string captured during initialization

### 11.2 Recent Attempts

`/api/v1/database/attempts` returns recent persisted attempts ordered by:

- `finalized_at_ms desc`
- `id desc`

This ordering reflects the intended meaning of the recent-attempt table:

- most recently finalized results first

### 11.3 Leaderboards

`/api/v3/leaderboards` joins the template reference list with current champion
rows to present one leaderboard entry per template.

### 11.4 Champion Name Claiming

`/api/v3/leaderboards/claim` updates only the current champion row for a
template, not arbitrary attempt history.

## 12. How The Webpage Uses The Database Layer

The webpage uses the database indirectly rather than speaking SQL, of course,
but it is tightly shaped by the persistence model.

The right-hand panel uses:

- `/api/v1/database/health`
  to show database availability
- `/api/v1/database/attempts?limit=15`
  to show recent finalized attempts
- `/api/v3/leaderboards`
  to show template champions
- `/api/v3/leaderboards/claim`
  to save champion names

This makes the webpage a presentation layer over persisted history rather than a
viewer of raw backend internals.

## 13. Why SQLite Was A Reasonable Choice

For the current system, SQLite is a reasonable choice because:

- the write rate is low relative to packet ingest
- only finalized attempts are persisted
- deployment and backup are simple
- the dataset is naturally small enough for a lab/demo system

The architecture still leaves room for a different SQL backend through
`DATABASE_URL`.

## 14. Operational Characteristics

### 14.1 Strengths

- simple deployment
- low administrative overhead
- strong fit for finalized-result persistence
- easy inspection during demos and development

### 14.2 Tradeoffs

- not designed as a high-concurrency analytical store
- active strokes are not durable until finalization
- SQLite may become a bottleneck if the system were scaled far beyond the
  current project scope

These tradeoffs are appropriate for the project’s goals.

## 15. Summary

The database layer is intentionally narrow in scope and well aligned with the
project architecture.

It does not try to be the real-time engine of the system. Instead, it provides:

- durable finalized-attempt history
- leaderboard support
- champion naming
- operationally useful historical views for the webpage

That makes it a strong complement to the in-memory live runtime rather than a
replacement for it.
