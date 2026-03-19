# Cloud Backend Reports

This folder contains detailed backend-facing reports for the deployed Wand
Brain cloud application.

## Reports

- [backend_system_report.md](./backend_system_report.md)
  high-level backend architecture report, including how the live runtime, the
  webpage, and the database fit together.
- [webpage_architecture_report.md](./webpage_architecture_report.md)
  detailed report on the live dashboard webpage, its polling model, and how it
  consumes the backend APIs.
- [database_architecture_report.md](./database_architecture_report.md)
  detailed report on the persistence layer, data model, and finalize-time
  database workflow.

## Core Source References

- [`../main.py`](../main.py)
- [`../frontend/index.html`](../frontend/index.html)
- [`../database/database.py`](../database/database.py)
- [`../database/models.py`](../database/models.py)
- [`../backend/versions/brain_v2_scoring/src/brain/api/server.py`](../backend/versions/brain_v2_scoring/src/brain/api/server.py)
- [`../../protocol/protocol/brain-web_api.md`](../../protocol/protocol/brain-web_api.md)
- [`../../protocol/protocol/brain_api/README.md`](../../protocol/protocol/brain_api/README.md)

## Reading Order

For a clean presentation, read them in this order:

1. [backend_system_report.md](./backend_system_report.md)
2. [webpage_architecture_report.md](./webpage_architecture_report.md)
3. [database_architecture_report.md](./database_architecture_report.md)
