# Cloud Backend

This directory holds the backend-side source for the Wand Brain service.

## Canonical Runtime

The canonical live runtime is:

- [versions/brain_v2_scoring/src/brain](versions/brain_v2_scoring/src/brain)

That tree contains the modules for:

- UDP receive
- packet parsing
- live attempt state
- rasterization
- template scoring

Key files:

- [versions/brain_v2_scoring/src/brain/api/server.py](versions/brain_v2_scoring/src/brain/api/server.py)
- [versions/brain_v2_scoring/src/brain/ingest/parser.py](versions/brain_v2_scoring/src/brain/ingest/parser.py)
- [versions/brain_v2_scoring/src/brain/render/rasterize.py](versions/brain_v2_scoring/src/brain/render/rasterize.py)
- [versions/brain_v2_scoring/src/brain/scoring/similarity.py](versions/brain_v2_scoring/src/brain/scoring/similarity.py)

## Related Docs

The protocol and API documentation that explains this runtime is here:

- [../../protocol/protocol/pynq-udp-brian-v1.md](../../protocol/protocol/pynq-udp-brian-v1.md)
- [../../protocol/protocol/pynq-udp-flow.md](../../protocol/protocol/pynq-udp-flow.md)
- [../../protocol/protocol/brain-web_api.md](../../protocol/protocol/brain-web_api.md)
- [../../protocol/protocol/brain_api/README.md](../../protocol/protocol/brain_api/README.md)

## Deployment Note

On EC2, this runtime is copied into `cloud/alt_live_console/brain_runtime` for
deployment. That deployed copy should not be treated as the canonical GitHub
source tree.
