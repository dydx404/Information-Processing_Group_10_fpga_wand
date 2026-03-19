# Runtime Data

This directory is for runtime-generated local data.

Examples:

- `fpgawand.sqlite3`
- `node_control_state.json`
- rendered attempt images under `outputs/`
- copied runtime templates under `templates/`

These files are useful for local backup and debugging, but they are not the
canonical source for GitHub commits.

This folder may also contain runtime snapshots copied back from EC2 during
deployment recovery or pre-commit cleanup. Keep those files local unless you
explicitly intend to publish sample data.
