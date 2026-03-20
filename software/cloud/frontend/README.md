# Frontend

The live console UI is implemented as a single polling page:

- [index.html](index.html)

It is served directly by the FastAPI app in [../main.py](../main.py).

## What It Shows

- live wand state
- live and finalized drawings
- template selection
- node control and ack state
- recent attempts
- leaderboards
- stroke timing

## Why It Matters

The frontend is the operator-facing surface of the project. It turns the
backend from a raw ingest service into something that can be:

- demonstrated live
- inspected during integration
- controlled during multi-node tests
- used to validate whether packets, attempts, and scoring are behaving as
  expected

The frontend is intentionally simple and debuggable: it uses HTTP polling
rather than a separate SPA framework or WebSocket stack.

For the backend routes that power these panels, see:

- [../../protocol/protocol/brain-web_api.md](../../protocol/protocol/brain-web_api.md)
- [../../protocol/protocol/brain_api/live_runtime_and_plotting.md](../../protocol/protocol/brain_api/live_runtime_and_plotting.md)
- [../../protocol/protocol/brain_api/node_control.md](../../protocol/protocol/brain_api/node_control.md)

For a fuller architecture write-up of the webpage itself, see:

- [../report/webpage_architecture_report.md](../report/webpage_architecture_report.md)
