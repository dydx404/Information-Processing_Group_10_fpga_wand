# Cloud Infrastructure Notes

This folder is for deployment and environment notes rather than application
logic.

## Current EC2 Shape

The live service is typically exposed as:

- HTTP API and dashboard on port `8000`
- UDP ingest on port `41000`

## Launch Path

The repo-level launcher is:

- [cloud/start_script.sh](../start_script.sh)

On EC2, the deployed runtime is launched from a copied directory under
`cloud/alt_live_console/start_script.sh`.

If the EC2 public IP changes, update the PYNQ sender configuration or set the
`BRAIN_HOST` environment variable on the board-side demo rather than editing the
cloud service code itself.

## Deployment Principle

For GitHub, keep the canonical source in the repo tree under [cloud/](../).

Treat `cloud/alt_live_console` on EC2 as deployment state, not the long-term
source of truth.
