# Final Runbook

This runbook is the shortest practical path for launching and checking the
final adopted FPGA-Wand system.

It is written for someone who wants to run the project, verify that the main
data path works, and understand what “healthy” looks like.

---

## Final-System Components

The final system has two active runtime sides:

1. **Cloud side**
   Wand Brain on EC2 or a local machine
2. **Node side**
   PYNQ runtime on one or more boards

The basic interaction is:

- PYNQ sends UDP point packets to Wand Brain
- Wand Brain serves the live dashboard over HTTP
- PYNQ polls HTTP control state from Wand Brain

---

## Default Ports

- `8000/tcp`
  live console and HTTP APIs
- `41000/udp`
  point-stream ingest from PYNQ nodes

---

## 1. Start The Cloud Side

From the repository root:

```bash
cd software/cloud
bash start_script.sh --install-deps
```

Expected result:

- the FastAPI app starts successfully
- the dashboard becomes available at `http://127.0.0.1:8000/`

Basic health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response shape:

```json
{"ok": true, "...": "..."}
```

---

## 2. Prepare The PYNQ Node

The main node runtime is:

- [../../FPGA/runtime/pynq_wand_brain_demo.py](../../FPGA/runtime/pynq_wand_brain_demo.py)

Before running it, confirm:

- the correct `.bit` / `.hwh` files are available on the board
- the camera is connected and readable
- `BRAIN_HOST` points to the correct Wand Brain host
- each board has a unique:
  - `DEVICE_NUMBER`
  - `WAND_ID`

If needed, the cloud host can be overridden through `BRAIN_HOST`.

---

## 3. Run The PYNQ Node

Launch the board-side runtime from the PYNQ environment using the current
configured demo path.

What healthy startup looks like:

- overlay loads successfully
- DMA IP is found
- centroid IP is found
- camera opens successfully
- Wand Brain health check succeeds

The most useful startup stages are:

- `Loading overlay...`
- `Allocating DMA buffer...`
- `Opening camera...`
- `Opening Wand-Brain bridge...`
- `Checking Wand-Brain health...`

If startup stops consistently at one of those steps, the fault is usually local
to that subsystem.

---

## 4. Check The Dashboard

Open:

```text
http://127.0.0.1:8000/
```

Healthy behaviour:

- wand entries appear in the UI
- the live drawing area updates while the wand is active
- finalized attempts appear after stroke completion
- scores and templates update after finalization
- node control state is visible if the node-control-enabled runtime is in use

---

## 5. Useful Verification Paths

### Health only

```bash
curl http://127.0.0.1:8000/api/v1/health
```

### Live wand list

```bash
curl http://127.0.0.1:8000/api/v1/wands
```

### Node connectivity and UDP check

```bash
python3 software/tools/wb_connection_check.py --host 127.0.0.1 --udp-port 41000 --api-port 8000
```

### End-to-end smoke test

```bash
python3 software/tools/full_system_smoke_test.py --host 127.0.0.1 --udp-port 41000 --api-port 8000
```

---

## 6. Healthy-System Checklist

The system is behaving correctly if the following are true:

- `api/v1/health` returns success
- the PYNQ node can complete startup
- UDP points appear as live attempts
- finalized attempts render to images
- the dashboard updates without manual refresh
- control changes can be observed on node-aware runtimes

---

## 7. Common Failure Points

### Cloud starts, but no live drawing appears

Check:

- PYNQ `BRAIN_HOST`
- UDP port `41000`
- whether the node is actually sending valid points

### Overlay loads, but node does not move past camera startup

Check:

- camera device availability
- camera index
- board-side OpenCV / capture state

### Packets appear, but the wrong node identity shows up

Check:

- `DEVICE_NUMBER`
- `WAND_ID`
- whether another board is still transmitting

### Dashboard loads, but node control does not apply

Check:

- whether the running node runtime includes the HTTP control polling logic
- whether the selected board is using the current `pynq_udp_bridge.py`

---

## 8. Best Supporting Files

If you need to go one level deeper after this runbook, open:

- [../../FPGA/runtime/ps_pl_flow.md](../../FPGA/runtime/ps_pl_flow.md)
- [../../software/protocol/protocol/pynq-udp-flow.md](../../software/protocol/protocol/pynq-udp-flow.md)
- [../../software/cloud/report/backend_system_report.md](../../software/cloud/report/backend_system_report.md)
