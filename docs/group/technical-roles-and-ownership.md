# Technical Roles and Ownership Structure

This document defines the technical role structure for the FPGA-Wand project.
Work is divided into three concrete engineering tracks that together form the
complete system.

Each track has clearly defined responsibilities, deliverables, and boundaries.
This structure is designed to support parallel development while maintaining
integration stability and accountability.

---

## Overview of the Three Technical Tracks

The project is organised into the following three tracks:

1. **ESP32 / Raw Data Collection**
2. **FPGA Hardware Design & Node-Side Processing (Jupyter/PYNQ)**
3. **Cloud Backend & Database**

Each track:
- Owns a well-defined part of the system
- Delivers concrete, testable outputs
- Integrates with the other tracks through agreed interfaces

---

## Track 1 — ESP32 / Raw Data Collection

### Scope
This track is responsible for all **sensor-side functionality** on the wand.

### Responsibilities
- IMU or sensor interfacing (I2C/SPI)
- Sampling and timestamping of raw motion data
- Basic preprocessing (e.g. scaling, filtering if needed)
- Packaging and transmitting data or events to the backend
- Receiving configuration updates from the backend (if applicable)
- Power supply and other considerations

### Explicit Non-Responsibilities
- Gesture classification logic
- FPGA acceleration
- Cloud-side decision making

### Deliverables
- ESP32 firmware that reliably produces raw or lightly processed motion data
- Verified data transmission to the backend
- Documentation of data format and sampling behaviour

### Success Criterion
> Moving the wand produces consistent, time-aligned data that reaches the cloud.

---

## Track 2 — FPGA Hardware Design & Node-Side Processing

### Scope
This track is responsible for **local processing on the node**, including both
software and hardware acceleration paths.

### Responsibilities
- Node-side processing logic (Python/Jupyter on PYNQ)
- Gesture detection and classification (circle as minimum demo)
- Software-only baseline implementation
- FPGA hardware design (Vivado) for acceleration or optimisation
- Drivers and interfaces between FPGA and node software
- Performance and resource usage measurement

### Explicit Non-Responsibilities
- Raw sensor acquisition
- Cloud session logic or persistence

### Deliverables
- Working local gesture classification pipeline
- Clear comparison between software and FPGA-accelerated paths (if implemented)
- Resource utilisation and performance metrics
- Reproducible demo notebooks or scripts

### Success Criterion
> The node can locally determine whether a gesture (e.g. circle) was performed
> and report the result correctly.

---

## Track 3 — Cloud Backend & Database

### Scope
This track is responsible for all **server-side functionality**.

### Responsibilities
- API or WebSocket server
- Multi-node session management
- Receiving events or data from nodes
- Sending configuration or state updates back to nodes
- Database schema and persistence
- Logging for testing and evaluation

### Explicit Non-Responsibilities
- Sensor handling
- Local signal processing
- FPGA design

### Deliverables
- Backend server that supports multiple simultaneous nodes
- Reliable bidirectional communication
- Database storing relevant state and logs
- Deployment-ready backend (local or EC2)

### Success Criterion
> Two or more nodes can communicate with the server and receive state updates
> that affect their behaviour.

---

## Cross-Track Integration Rules

- Track interfaces must be documented (data format, message schema)
- No track may silently change an interface without coordination
- End-to-end demos take priority over internal optimisation
- Software baselines must exist before hardware optimisation

---

## Project Lead and Integration Role

One member acts as **Project Lead / Integrator**.

Responsibilities:
- Maintain architectural consistency across tracks
- Decide interface changes and scope adjustments
- Run milestone reviews and accept demos
- Coordinate merges and feature freezes

The Project Lead may actively contribute to **any one technical track** while
retaining responsibility for overall integration.

---

## Definition of Done (All Tracks)

A task is considered complete only when:
- The code runs as intended
- The output can be demonstrated
- The change is integrated without breaking other tracks
- Relevant documentation is updated if needed

---

## Summary

This role structure ensures:
- Clear technical ownership
- Parallel development without confusion
- Predictable integration
- Fair and visible contributions

All development is coordinated through GitHub issues, branches, and pull requests.
