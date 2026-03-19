# Technical Roles and Ownership Structure  
**FPGA-Wand Project**

This document defines the **technical ownership, responsibility boundaries, and integration rules** for the FPGA-Wand project.

The system is a **distributed point-tracking and shape recognition system**, not a gesture-recognition system.  
All design, implementation, and evaluation are based on **explicit spatial tracking and deterministic processing**, rather than learned or semantic gesture inference.

The project is developed across **three concrete engineering tracks**, each owning a clearly scoped subsystem with well-defined inputs and outputs.

This structure is designed to:

- Enable parallel development  
- Prevent responsibility overlap  
- Preserve interface stability  
- Support incremental, testable milestones  

---

## Overview of Technical Tracks

The project is organised into the following tracks:

1. **Optical Wand and Camera Setup** (LED Wand + Camera)  
2. **FPGA Node & Local Processing** (PYNQ-Z1 / Local Runtime)  
3. **Backend, Database & User Interface** (System-level coordination)  

The **FPGA node (PYNQ-Z1)** is the primary processing and decision-making node, as defined by the coursework specification.

The **LED wand + camera setup** together form the optical sensing subsystem
that feeds the FPGA node.

The **Backend, Database, and UI** provide coordination, persistence, and interaction, but are not required for the minimum viable demonstration.

---

## Track 1 — Optical Wand and Camera Setup  
**Owners: Yi, Ananya**

### Scope

This track owns the **physical wand visibility setup and camera-side optical
tracking conditions**.

Its responsibility is to make the physical wand and camera setup produce a
stable bright target that the FPGA node can track reliably.

This track does **not** perform shape recognition or semantic interpretation.

---

### Responsibilities

- Camera setup and calibration  
- Detection of the wand marker (visible LED)  
- Stable physical positioning and optical visibility  
- Lighting and background conditions that support robust tracking  
- Calibration support for the camera/FPGA pipeline  
- Power stability and hardware reliability  

---

### Explicit Non-Responsibilities

- Shape or path classification  
- Path reconstruction or normalisation  
- FPGA hardware design or acceleration  
- Cloud communication  
- User-facing interfaces  

---

### Data Outputs (to FPGA Node)

This track does not define a separate embedded protocol of its own in the final
system. Instead, it provides the physical conditions under which the FPGA node’s
camera pipeline can generate stable 2D tracking results.

---

### Deliverables

- Reliable camera-based optical tracking conditions  
- Wand visibility and alignment notes  
- Calibration and validation notes  

---

### Success Criterion

Moving the LED wand through the tracked space produces:

- stable and visible optical tracking conditions  
- repeatable camera observations of the wand tip  
- usable centroid data on the FPGA node  

---

## Track 2 — FPGA Node & Local Processing  
**Owners: Mingze, Wills**

### Scope

This track owns all **node-side processing, reconstruction, classification, and real-time visual output**.

The **PYNQ-Z1** is the authoritative local processing node and must operate correctly **without backend support**.

---

### Responsibilities

#### Node-Side Software (Processing System)

- Camera frame capture and preprocessing  
- DMA and MMIO orchestration  
- Reading centroid statistics from the PL  
- Filtering and accepting tracked points  
- Local sketch rendering  
- UDP transmission to the backend  
- HTTP node-control polling and acknowledgement  
- Optional local status output for debugging and demo use  

---

#### FPGA Hardware (Programmable Logic)

- Optional acceleration of deterministic processing:
- Filtering or smoothing  
- Feature extraction  
- Distance / error accumulation  
- AXI streaming and DMA interfaces  
- Fixed-point optimisation  
- Performance and resource utilisation measurement  

> A correct software baseline **must exist** before FPGA acceleration.

---

### Explicit Non-Responsibilities

- Sensor acquisition  
- Camera tracking or calibration  
- Backend session management  
- Web-based user interfaces  

---

### Deliverables

- Working local reconstruction and classification pipeline  
- HDMI demo showing live drawing and results  
- FPGA design (if used) with measured benefit  
- Software vs hardware performance comparison  
- Reproducible Jupyter notebooks or scripts  

---

### Success Criterion

The FPGA node can:

- Reconstruct a 2D drawing locally  
- Classify a basic shape (line or circle)  
- Display results in real time via HDMI  

---

## Track 3 — Backend, Database & User Interface  
**Owner: Ellie**  
**Contributors: Seth, Apshara**

### Scope

This track owns all **system-level coordination, persistence, and user-facing interaction**.

It enables multi-node behaviour and extended demonstrations but is **not required for the minimum demo**.

---

### Responsibilities

- Backend server (HTTP + UDP ingest)  
- Multi-node session management  
- Receiving classification results and events from FPGA nodes  
- Sending configuration or mode updates to nodes  
- Database schema and persistence  
- System-level logging and replay  
- User-facing web interface  
- Visualisation of drawings and results  
- System state display  
- Optional competitive or collaborative logic  
- Deployment (local or EC2)  

---

### Explicit Non-Responsibilities

- Sensor handling  
- Vision or tracking logic  
- FPGA or hardware design  
- Real-time HDMI rendering  

---

### Deliverables

- Backend server supporting multiple FPGA nodes  
- Reliable bidirectional communication  
- Database storing system state and results  
- User-facing web interface  
- Deployment and usage documentation  

---

### Success Criterion

Multiple FPGA nodes can:

- Connect to the backend  
- Affect shared system state  
- Be observed and interacted with through a web interface  

---

## Cross-Track Integration Rules

- All interfaces **must be documented** in `software/protocol/`  
- No track may change an interface unilaterally  
- End-to-end demos take priority over internal optimisation  
- Software baselines precede FPGA acceleration  
- Camera-derived 2D position is the **authoritative spatial reference**  

---

## Project Lead & Integration Authority

One member acts as **Project Lead / System Integrator**.

### Responsibilities

- Maintain architectural consistency  
- Approve interface and scope changes  
- Run milestone reviews and accept demos  
- Coordinate merges and feature freezes  

The Project Lead may contribute to a technical track while retaining **final integration authority**.

---

## Definition of Done (All Tracks)

A task is complete only when:

- Functionality works as intended  
- Output can be demonstrated  
- Integration with other tracks is verified  
- Relevant documentation is updated  

This definition applies to **all tracks equally**.
