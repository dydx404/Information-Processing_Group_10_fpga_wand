# Newcomer Guide

This guide is for someone opening the FPGA-Wand repository for the first time
and trying to answer one question quickly:

`What is this project, where is the real implementation, and what should I read first?`

---

## One-Sentence Summary

FPGA-Wand is a camera-based drawing system in which a PYNQ-Z1 extracts
centroid-style wand positions and streams them to a cloud service that renders,
scores, stores, and displays the result live.

---

## What Is Final And What Is Background

The repo contains both:

- the **final adopted system**
- earlier or exploratory material that helped the project evolve

If you only want to understand the final demonstrated system, focus on:

- [../FPGA/](../FPGA/)
- [../software/](../software/)
- [architecture/overview.md](architecture/overview.md)
- [testing/system_validation_report.md](testing/system_validation_report.md)

Use the `group/` subtree mainly for report-writing, planning, and contribution
tracking rather than for the runtime architecture itself.

---

## The 10-Minute Reading Path

Read these in order:

1. [../README.md](../README.md)
   the high-level system and repo map
2. [architecture/overview.md](architecture/overview.md)
   the architecture at a system level
3. [../FPGA/runtime/ps_pl_flow.md](../FPGA/runtime/ps_pl_flow.md)
   the detailed PS/PL flow on the PYNQ board
4. [../software/protocol/protocol/pynq-udp-flow.md](../software/protocol/protocol/pynq-udp-flow.md)
   how a point travels from PYNQ to the cloud
5. [../software/cloud/report/backend_system_report.md](../software/cloud/report/backend_system_report.md)
   how the backend/web/database side fits together

If you complete those five reads, you will understand most of the final system.

---

## Choose Your Entry Point

### If you care about FPGA first

Start with:

- [../FPGA/README.md](../FPGA/README.md)
- [../FPGA/runtime/pynq_wand_brain_demo.py](../FPGA/runtime/pynq_wand_brain_demo.py)
- [../FPGA/runtime/pynq_udp_bridge.py](../FPGA/runtime/pynq_udp_bridge.py)
- [../FPGA/designs/centroid_pipeline/used_version/README.md](../FPGA/designs/centroid_pipeline/used_version/README.md)

### If you care about the backend first

Start with:

- [../software/cloud/README.md](../software/cloud/README.md)
- [../software/cloud/main.py](../software/cloud/main.py)
- [../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py](../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- [../software/cloud/frontend/index.html](../software/cloud/frontend/index.html)

### If you care about the protocol first

Start with:

- [../software/protocol/README.md](../software/protocol/README.md)
- [../software/protocol/protocol/pynq-udp-brian-v1.md](../software/protocol/protocol/pynq-udp-brian-v1.md)
- [../software/protocol/protocol/brain-web_api.md](../software/protocol/protocol/brain-web_api.md)

### If you care about testing and proof first

Start with:

- [testing/system_validation_report.md](testing/system_validation_report.md)
- [testing/test-plan.md](testing/test-plan.md)
- [../software/tools/README.md](../software/tools/README.md)

---

## The Final System In Plain Terms

The final adopted system has four main stages:

1. **Physical sensing**
   the LED wand tip is seen by the camera
2. **Node-side reduction**
   the PYNQ PS and PL reduce the image to a tracked centroid point
3. **Cloud reconstruction**
   Wand Brain receives point packets, reconstructs strokes, renders images, and
   scores them
4. **User-facing operation**
   the web console shows live drawings, attempts, templates, control state, and
   leaderboards

---

## Important Distinctions

### Canonical source vs runtime artefacts

The source of truth is the code and documentation under:

- [../FPGA/](../FPGA/)
- [../software/](../software/)
- [../docs/](../docs/)

Do not confuse those with runtime artefacts such as:

- local SQLite databases
- rendered output images
- EC2 deployment copies
- temporary logs

### Adopted system vs exploratory paths

Some parts of the repository history document earlier ideas and MVP-stage work.
That material can be useful context, but it should not be confused with the
final adopted model.

For final-system understanding, prioritize:

- the centroid-based FPGA path
- the PYNQ runtime in `FPGA/runtime/`
- the Wand Brain service in `software/cloud/`

---

## Fast Orientation By Folder

| Folder | What it is for | Read first |
| --- | --- | --- |
| [../hardware/](../hardware/) | physical build notes | [../hardware/README.md](../hardware/README.md) |
| [../FPGA/](../FPGA/) | PYNQ runtime and FPGA design | [../FPGA/README.md](../FPGA/README.md) |
| [../software/](../software/) | backend, protocols, tools | [../software/README.md](../software/README.md) |
| [group/](group/) | project-management and report-prep notes | [group/project_management_section_template.md](group/project_management_section_template.md) |

---

## If You Want To Run Something

### Cloud side

```bash
cd ../software/cloud
bash start_script.sh --install-deps
```

Then open:

```text
http://127.0.0.1:8000/
```

### PYNQ side

The main node demo is:

- [../FPGA/runtime/pynq_wand_brain_demo.py](../FPGA/runtime/pynq_wand_brain_demo.py)

---

## Best First Question To Ask

If you only have a few minutes, ask:

`What is the final adopted path from camera frame to browser view?`

The answer is spread across exactly these files:

- [../FPGA/runtime/pynq_wand_brain_demo.py](../FPGA/runtime/pynq_wand_brain_demo.py)
- [../FPGA/designs/centroid_pipeline/used_version/source/frame_centroid.v](../FPGA/designs/centroid_pipeline/used_version/source/frame_centroid.v)
- [../software/protocol/protocol/pynq-udp-flow.md](../software/protocol/protocol/pynq-udp-flow.md)
- [../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py](../software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
- [../software/cloud/frontend/index.html](../software/cloud/frontend/index.html)
