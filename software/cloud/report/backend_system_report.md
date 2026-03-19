# Wand Brain Cloud Backend System Report

## 1. Purpose And Scope

This report describes the architecture of the deployed Wand Brain cloud
backend. It focuses on the parts most visible in the final system:

- the live webpage served to users and operators
- the database used for persistence and leaderboards
- the runtime service that ties live UDP ingestion, rendered images, scoring,
  and persistence together

The report is grounded in the current source tree:

- app wrapper: [`../main.py`](../main.py)
- live runtime: [`../backend/versions/brain_v2_scoring/src/brain/api/server.py`](../backend/versions/brain_v2_scoring/src/brain/api/server.py)
- frontend: [`../frontend/index.html`](../frontend/index.html)
- persistence layer: [`../database/database.py`](../database/database.py),
  [`../database/models.py`](../database/models.py)

## 2. Backend Composition

The cloud backend is intentionally built in two layers.

### 2.1 Base Live Runtime

The base runtime lives in:

- [`../backend/versions/brain_v2_scoring/src/brain/api/server.py`](../backend/versions/brain_v2_scoring/src/brain/api/server.py)

This layer owns:

- UDP packet reception
- packet parsing
- live attempt buffering in memory
- live PNG rendering
- finalized attempt rendering
- template scoring primitives
- the core `/api/v1/*` and `/api/v2/*` live routes

This layer is best understood as the real-time Brain engine.

### 2.2 Cloud Wrapper Layer

The wrapper layer lives in:

- [`../main.py`](../main.py)

This layer composes the live runtime with higher-level application features:

- frontend HTML serving
- database initialization
- finalized-attempt persistence
- per-wand target-template selection
- node-control APIs
- leaderboard APIs
- database inspection routes

This split is architecturally important. It lets the real-time engine remain
focused on ingestion and rendering, while the wrapper adds persistence and UI
features without overloading the core runtime module.

## 3. Main Responsibilities Of The Backend

At system level, the backend performs four major jobs.

### 3.1 Live Ingestion

The backend receives UDP point packets from PYNQ boards on port `41000`, parses
them, and reconstructs active attempts in memory.

### 3.2 Live Visualization

As points arrive, the backend periodically rasterizes them into a live PNG so
the webpage can show the current drawing without waiting for stroke
finalization.

### 3.3 Finalization And Scoring

When a stroke ends, or times out, the backend finalizes the attempt, renders a
final PNG, computes its score against templates, and updates the in-memory
latest-attempt views.

### 3.4 Persistence And Presentation

The wrapper persists finalized attempts into the SQL database, updates template
champions, and serves the webpage plus all API endpoints used by the dashboard.

## 4. End-To-End Backend Data Flow

The full backend pipeline can be summarized as:

1. a PYNQ node sends UDP point packets
2. the live runtime receives and parses those packets
3. the runtime appends points into an in-memory attempt buffer
4. the runtime periodically renders a live image
5. the runtime finalizes a stroke on explicit end or idle timeout
6. the wrapper scores and persists the finalized result
7. the webpage polls HTTP endpoints to display live state, finalized results,
   and database-backed history

The critical architectural distinction is:

- live activity is handled in memory first
- historical records are written to the database only after finalization

## 5. Service Structure And Directory Layout

The most important backend-facing directories are:

- [`../frontend/`](../frontend/)
  the single-page dashboard
- [`../database/`](../database/)
  SQLAlchemy configuration and ORM models
- [`../backend/`](../backend/)
  live runtime packages
- [`../data/`](../data/)
  runtime state and persisted files

Within those:

- [`../frontend/index.html`](../frontend/index.html)
  is the whole webpage UI
- [`../database/database.py`](../database/database.py)
  configures the database engine and session factory
- [`../database/models.py`](../database/models.py)
  defines persisted tables
- [`../data/fpgawand.sqlite3`](../data/fpgawand.sqlite3)
  is the default SQLite database file
- [`../data/node_control_state.json`](../data/node_control_state.json)
  stores operational node-control state

## 6. API Surface Of The Backend

The served API families are documented in:

- [`../../protocol/protocol/brain-web_api.md`](../../protocol/protocol/brain-web_api.md)
- [`../../protocol/protocol/brain_api/README.md`](../../protocol/protocol/brain_api/README.md)

At a high level:

- `/api/v1/*` exposes live runtime status and recent finalized-attempt views
- `/api/v2/*` exposes templates, template selection, and scoring
- `/api/v3/*` exposes node control and leaderboards

The webpage is therefore not tightly coupled to internal Python objects. It is
driven entirely by the backend’s HTTP contract.

## 7. Relationship Between Webpage And Backend

The webpage is served by the same FastAPI process that owns the live runtime and
the persistence wrapper.

This has several consequences:

- the UI and API share one deployment unit
- there is no separate frontend build pipeline
- the webpage can be refreshed and debugged with simple browser tools
- the operational model stays simple for a lab/demo environment

The page is mounted through:

- `/`
- `/frontend/*`

This is done in [`../main.py`](../main.py) using `FileResponse` and
`StaticFiles`.

## 8. Relationship Between Backend And Database

The backend does not use the database as a hot real-time buffer.

Instead:

- live points stay in runtime memory while a stroke is active
- only finalized attempts become database rows
- leaderboards are derived from scored finalized attempts

This design reduces write pressure on the database and keeps the ingest path
simple.

It also means the system behaves gracefully if the database becomes temporarily
unavailable:

- live drawing can still continue
- persistence-oriented views degrade separately

## 9. State Separation Strategy

One of the strongest design decisions in the backend is the separation between
three kinds of state.

### 9.1 Live Drawing State

Stored in memory inside the live runtime:

- current attempt buffers
- current wand status
- live image paths
- most recent parsed event

### 9.2 Historical Persistent State

Stored in SQL:

- finalized attempts
- template champions

### 9.3 Operational Control State

Stored in JSON:

- node control objects
- node acknowledgement objects

This separation makes the system easier to reason about:

- high-frequency data stays lightweight and local to the runtime
- historical records are durable and queryable
- operational control can evolve independently of the relational schema

## 10. Why The Backend Uses Polling For The Webpage

The webpage is a polling dashboard rather than a push/WebSocket application.

This was a pragmatic architectural choice:

- easier to debug during development
- sufficient for the project’s update rates
- fewer moving parts in deployment
- simpler synchronization model between frontend and backend

The backend therefore serves:

- small JSON snapshots
- live PNG files
- finalized PNG files

rather than maintaining a persistent browser connection.

## 11. Backend Strengths

The current architecture has several practical strengths.

### 11.1 Clear Separation Of Concerns

The live runtime, persistence wrapper, webpage, and database each have a
recognizable role.

### 11.2 Real-Time But Simple

The system achieves live visualization and control without requiring a more
complex real-time web stack.

### 11.3 Resilient Integration Boundary

The UDP data plane and HTTP control/presentation plane are separate, which keeps
protocol responsibilities clean.

### 11.4 Strong Demo Value

Because finalized attempts are persisted and leaderboards are maintained, the
backend supports both live demonstrations and historical evidence of use.

## 12. Known Tradeoffs

The architecture also makes a few explicit tradeoffs.

### 12.1 Single-Process Simplicity

Serving the webpage, APIs, and runtime from one process is convenient, but it
is not a horizontally scaled microservice design.

### 12.2 In-Memory Live State

If the service restarts, active in-progress strokes are lost. Only finalized
history remains.

### 12.3 Polling Over Push

Polling is simpler than WebSockets, but it introduces repeated requests and
slightly delayed UI updates compared with a push-based design.

These tradeoffs are reasonable for the project and align with the design goal
of reliable integration over maximal infrastructure complexity.

## 13. Recommended Companion Reports

For deeper treatment of the two main user-facing backend components, read:

- [webpage_architecture_report.md](./webpage_architecture_report.md)
- [database_architecture_report.md](./database_architecture_report.md)
