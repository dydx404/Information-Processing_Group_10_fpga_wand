# Group Allocations and Week 1 Tasks  (deadline 2.22)
**Project:** FPGA Wand — Information Processing  
**Milestone:** Milestone 1 — End-to-End Connectivity

This document defines the subgroup structure, responsibilities, and Week 1 tasks.
Each subgroup is responsible for delivering concrete outputs. If a deliverable is
not committed to the repository, the task is considered incomplete.

---

## Subgroup 1 — ESP32 & Sensors

**Members**
- yi
- Ananya
- Apshara

**Scope**
This subgroup owns all components related to sensor-side data generation and
communication from the ESP32 to the FPGA node.

**Responsibilities**
- ESP32 firmware setup and flashing
- Sensor input (IMU or synthetic data)
- UART communication from ESP32 to PYNQ
- Motion segmentation (gesture start / stop)
- Local actuation feedback (LED / buzzer)

**Week 1 Tasks**
- Configure ESP32 development environment
- Generate stable sensor or synthetic motion data
- Transmit framed data over UART at a fixed rate
- Implement segment start/end detection
- Implement actuation response to commands from PYNQ

**Week 1 Deliverables**
- ESP32 sends UART data reliably to PYNQ
- Segment start/end events are visible
- Actuation commands change ESP32 behaviour
- Documentation explaining flashing, wiring, and testing

**Required Output**
- ESP32 source code committed
- `docs/esp32/README.md`

---

## Subgroup 2 — FPGA Node & Jupyter Processing

**Members**
- Wells
- Mingze Chen

**Scope**
This subgroup owns the FPGA-based node and all local processing required by the
coursework specification.

**Responsibilities**
- PYNQ-Z1 setup and configuration
- UART receiver on PYNQ
- Local data buffering and baseline processing
- Jupyter Notebook-based demonstration
- Handling configuration updates affecting local behaviour

**Week 1 Tasks**
- Set up PYNQ-Z1 environment
- Receive and parse UART data from ESP32
- Buffer motion segments on the node
- Implement a minimal local processing pipeline
- Demonstrate behaviour change in response to configuration updates

**Week 1 Deliverables**
- PYNQ reliably receives ESP32 data
- Local processing occurs on the node
- Node behaviour changes when configuration is updated
- Working Jupyter Notebook demo

**Required Output**
- Node-side scripts/notebooks committed
- `docs/node/processing_pipeline.md`

---

## Subgroup 3 — Backend & Cloud

**Members**
- Ellie
- Seth

**Scope**
This subgroup owns the cloud backend that communicates with FPGA nodes.

**Responsibilities**
- Backend server implementation
- Node registration and identification
- Receiving node data
- Broadcasting configuration updates
- Event logging (in-memory or database)

**Week 1 Tasks**
- Set up a minimal backend server
- Implement endpoint(s) to receive node data
- Implement configuration broadcast mechanism
- Log node activity and events

**Week 1 Deliverables**
- Backend server runs locally
- At least two nodes can connect
- Backend can send configuration updates
- Node behaviour changes in response to backend messages

**Required Output**
- Backend source code committed
- `docs/backend/README.md`

---

## Subgroup 4 — Testing, Demo & Documentation

**Members**
- Apshara
- Seth

**Scope**
This subgroup ensures the system is testable, reproducible, and presentable.

**Responsibilities**
- Milestone 1 demo checklist
- Reproducibility testing
- System architecture documentation
- Support material for the final report

**Week 1 Tasks**
- Define a Milestone 1 demo checklist
- Run the demo following the checklist
- Record pass/fail results
- Create a system architecture diagram

**Week 1 Deliverables**
- Completed Milestone 1 demo checklist
- System architecture diagram (ESP32 → PYNQ → Backend)

**Required Output**
- `docs/testing/milestone1_checklist.md`
- Architecture diagram file (PNG or PDF)

---

## General Rules

- Each subgroup is jointly responsible for its deliverables
- Blockers must be raised early within the subgroup
- All work must be committed to the repository
- No deliverable means the task is not complete

---

## Week 1 Goal

By the end of Week 1, the system must demonstrate:
- Two FPGA nodes participating
- Bidirectional communication between node and backend
- Local processing on the FPGA node
- Configuration updates affecting node behaviour
