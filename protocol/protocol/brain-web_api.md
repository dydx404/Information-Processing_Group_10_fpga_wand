# Wand-Brain Web API Protocol (Core MVP – Simplified)
**Website (display-only) → Wand-Brain (same EC2)**  
**Protocol name:** `wand-brain-web-api-v1-core`  
**Status:** MVP / frozen  
**Scope:** Read-only APIs only

This document defines the **only five web-facing functions** the website needs.
There is **no control**, **no POST**, and **no user input** in MVP.

---

## 0. System Model (important for clarity)

- **Wand-Brain**  
  - Receives UDP points from PYNQ  
  - Builds attempts (one button-hold = one attempt)  
  - Renders image, computes score  
  - Exposes HTTP APIs below  

- **Webserver**  
  - Serves static HTML/JS  
  - Reverse-proxies `/api/*` to Wand-Brain  


`attempt_id` == UDP `stroke_id` (MVP meaning: one drawing attempt)

---

## 1. API List (Exactly 5 Functions)

| # | API | Method | Function |
|--:|-----|--------|----------|
| 1 | `/api/v1/health` | GET | Check Wand-Brain connection |
| 2 | `/api/v1/wands` | GET | Live status of all wands |
| 3 | `/api/v1/wand/{wand_id}` | GET | Live status of a single wand |
| 4 | `/api/v1/attempt/latest?wand_id=` | GET | Latest attempt result for a wand |
| 5 | `/api/v1/attempt/{attempt_id}/image.png` | GET | Rendered image of an attempt |

---

## 2. Common Conventions

- All APIs are **HTTP GET**
- JSON responses unless stated otherwise
- Time units: milliseconds (`*_ms`)
- HTTP status codes:
  - `200` OK
  - `400` Invalid request
  - `404` Not found

---

## 3. Data Models

### 3.1 WandStatus
```json
{
  "wand_id": 1,
  "active": true,
  "current_attempt_id": 12345,
  "last_point_ms": 1730000000123
}
```

Meaning:

- active = true → button currently held, attempt in progress

- current_attempt_id = null → idle


### 3.2 AttemptResult
```json
{
  "attempt_id": 12345,
  "wand_id": 1,
  "device_number": 2,

  "start_ms": 1730000000000,
  "end_ms": 1730000001500,
  "num_points": 94,

  "result": {
    "status": "processed",
    "best_template_id": "triangle_v1",
    "best_template_name": "Triangle",
    "score": 0.87
  },

  "image_png": "/api/v1/attempt/12345/image.png"
}
```
### result.status:

- pending → attempt ended, processing not finished

- processed → score + image ready

- failed → processing error


## 4. API Details (The Five Functions)
### 4.1 Check Connection / Health
```
GET /api/v1/health
```


- Verify Wand-Brain is running and reachable.

Response:

```json
{
  "ok": true,
  "service": "wand-brain",
  "version": "0.1.0",
  "time_ms": 1730000000456
}
```

### 4.2 Live Wand Status (All Wands)
```
GET /api/v1/wands
```
Purpose:

- Show live state of all wands on the website.

Response:
```json
{
  "time_ms": 1730000000456,
  "wands": [
    {
      "wand_id": 1,
      "active": true,
      "current_attempt_id": 12345,
      "last_point_ms": 1730000000123
    },
    {
      "wand_id": 2,
      "active": false,
      "current_attempt_id": null,
      "last_point_ms": 1729999999000
    }
  ]
}
```
### 4.3 Live Status of a Single Wand
```json
GET /api/v1/wand/{wand_id}
```
Purpose:

- Show live state of one wand (useful for per-player UI).

Response:
```json
{
  "wand_id": 1,
  "active": true,
  "current_attempt_id": 12345,
  "last_point_ms": 1730000000123
}
```

Errors:

- 404 if wand does not exist

### 4.4 Latest Attempt Result (Per Wand)
```json
GET /api/v1/attempt/latest?wand_id=<int>
```
Purpose:

- Display the most recent drawing attempt and its score.

Response:

- AttemptResult(see before)

Errors:

- 400 if wand_id missing or invalid

- 404 if no attempt exists yet

Notes:

- If the attempt is still being processed:

- result.status = "pending"

- image may not yet exist

4.5 Get Attempt Image
```json
GET /api/v1/attempt/{attempt_id}/image.png
```
Purpose:

- Retrieve the rendered drawing image for display.

Response:

- 200 OK with Content-Type: image/png

- 404 if image not ready or attempt does not exist

## 5. Recommended Website Polling Logic (MVP)

Every 250–500 ms:
```json
GET /api/v1/wands
```
Every 500–1000 ms (per wand shown):
```json
GET /api/v1/attempt/latest?wand_id=...
```
When attempt_id changes or result.status becomes processed:

Reload image with cache-busting:
```json
/api/v1/attempt/<attempt_id>/image.png?cb=<time_ms>
```