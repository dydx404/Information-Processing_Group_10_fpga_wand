## brain_v2_scoring

Versioned backend workspace for post-MVP work (keeps MVP `cloud/backend/brain` untouched).

### New in v2

- Template-based scoring prototype (`src/brain/scoring/similarity.py`)
- New APIs:
  - `GET /api/v2/templates`
  - `GET /api/v2/template/{template_id}/image.png`
  - `GET /api/v2/score/latest?wand_id=...&template_id=...`
  - `GET /api/v2/score/attempt/{attempt_id}?template_id=...`

### Quick start

```bash
cd cloud/backend/versions/brain_v2_scoring
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pillow
python tools/generate_templates.py
uvicorn brain.api.server:app --app-dir src --host 0.0.0.0 --port 8000
```

### Notes

- Put reference template PNG files in `data/templates/`.
- Scoring currently uses pixel overlap metrics (Dice + IoU + area ratio).
- This is intentionally isolated from MVP.
