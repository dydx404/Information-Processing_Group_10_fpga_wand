# Software

This directory contains the EC2-side software stack and software-facing support
material.

## If You Open One File First

For most newcomers, start with:

- [cloud/README.md](cloud/README.md)

Then move to the protocol docs to understand how the node and cloud service
talk to each other.

## Main Areas

- [cloud/](cloud/)
  the FastAPI-based Wand Brain service, database layer, and live console UI.
- [protocol/](protocol/)
  documented software contracts, especially the UDP point-stream and HTTP APIs.
- [tools/](tools/)
  smoke tests, synthetic senders, and operator/demo helpers.

## Start Here

- [cloud/README.md](cloud/README.md)
- [protocol/README.md](protocol/README.md)
- [tools/README.md](tools/README.md)

## Newcomer Route

If you want the shortest path through the software side, read:

1. [cloud/README.md](cloud/README.md)
2. [protocol/protocol/pynq-udp-flow.md](protocol/protocol/pynq-udp-flow.md)
3. [protocol/protocol/brain-web_api.md](protocol/protocol/brain-web_api.md)
4. [cloud/report/backend_system_report.md](cloud/report/backend_system_report.md)

This sequence takes you from the live data path to the served APIs and then to
the backend/database/frontend architecture.
