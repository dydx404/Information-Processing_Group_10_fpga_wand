# brain_v2_scoring

This is the canonical live-runtime package used by the current Wand Brain cloud
service.

## What It Contains

- UDP receiver and packet parser
- live attempt buffering
- live and finalized PNG rasterization
- template scoring
- v1/v2 HTTP APIs for live status, templates, and scoring

Key modules:

- `src/brain/api/server.py`
- `src/brain/ingest/parser.py`
- `src/brain/render/rasterize.py`
- `src/brain/scoring/similarity.py`

## Quick Start

```bash
cd software/cloud/backend/versions/brain_v2_scoring
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pillow numpy
python tools/generate_templates.py
uvicorn brain.api.server:app --app-dir src --host 0.0.0.0 --port 8000
```

## Notes

- Template PNGs live in `data/templates/`.
- Scores are currently overlap-based heuristics using Dice, IoU, and area
  ratio.
- The repo-level cloud app in `software/cloud/main.py` wraps this runtime with
  database persistence, leaderboards, node control, and the frontend.
