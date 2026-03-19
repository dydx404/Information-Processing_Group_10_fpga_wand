# HTTP Node Control

This adds a separate HTTP control plane from EC2 to each PYNQ node.

The drawing data path stays unchanged:
- PYNQ -> EC2 point stream: UDP `wb-point-v1`

The new control path is:
- PYNQ -> EC2 control fetch / ack: HTTP `/api/v3/node/...`

## Why this is safe

- It does not change the working UDP packet format.
- It does not change the live point parser.
- Control is versioned with `revision`.
- Risky profile changes can wait until the next stroke boundary.
- Each node reports back what revision it actually applied.

## EC2 Endpoints

- `GET /api/v3/node-controls`
- `GET /api/v3/node/{device_number}/control`
- `PUT /api/v3/node/{device_number}/control`
- `GET /api/v3/node/{device_number}/status`
- `POST /api/v3/node/{device_number}/ack`

## Control Payload

```json
{
  "enabled": true,
  "armed": true,
  "tx_enabled": true,
  "mode": "precision",
  "apply_on": "next_attempt",
  "vision": {
    "threshold": 210,
    "min_count": 3
  },
  "stroke": {
    "gap_timeout_ms": 1200,
    "max_jump": 90,
    "smoothing_alpha": 0.55
  },
  "commands": {
    "clear_sketch": true,
    "recalibrate": true
  }
}
```

## Current PYNQ Behavior

The PYNQ demo now polls control every `500 ms` and sends status ack every `1000 ms`.

Immediate effects:
- `enabled = false`: stop accepting points
- `armed = false`: stop active drawing logic
- `tx_enabled = false`: keep local processing alive but stop UDP transmission

Profile effects:
- `mode`
- `vision.threshold`
- `vision.min_count`
- `stroke.gap_timeout_ms`
- `stroke.max_jump`
- `stroke.smoothing_alpha`

One-shot commands:
- `clear_sketch`
- `recalibrate`

## Example

Set node 2 into precision mode for the next stroke:

```bash
curl -X PUT http://13.51.156.87:8000/api/v3/node/2/control \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "precision",
    "apply_on": "next_attempt",
    "vision": {"threshold": 215, "min_count": 2},
    "stroke": {"gap_timeout_ms": 1200, "max_jump": 90, "smoothing_alpha": 0.55}
  }'
```

Pause node 1 immediately:

```bash
curl -X PUT http://13.51.156.87:8000/api/v3/node/1/control \
  -H 'Content-Type: application/json' \
  -d '{"enabled": false, "apply_on": "immediate"}'
```
