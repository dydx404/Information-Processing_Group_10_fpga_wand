# Cloud Database

This package contains the persistence layer used by the cloud service.

## Files

- [database.py](database.py)
  configures SQLAlchemy and the default SQLite database path.
- [models.py](models.py)
  defines the persisted tables.

## Current Tables

### `Attempt`

Stores finalized historical drawing attempts, including:

- wand and device identity
- attempt timing
- point count
- rendered image path
- best template match
- score

### `TemplateChampion`

Stores the current top-scoring attempt for each template, plus an optional
claimed player name.

## Important Separation

The SQL database stores finalized history.

It does not store:

- raw UDP packets
- per-frame live attempt buffers
- node control state

Revisioned node control and ack state live separately in
[software/cloud/node_control.py](../node_control.py).

## Runtime Data

The default SQLite file is created under:

- `software/cloud/data/fpgawand.sqlite3`

That file is runtime data and should not normally be committed to GitHub.

For a fuller persistence-layer report, see:

- [../report/database_architecture_report.md](../report/database_architecture_report.md)
