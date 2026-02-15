# Technical Roles and Ownership Structure  
**FPGA-Wand Project**

This document defines the technical ownership and responsibility structure for the **FPGA-Wand** project.

The system is developed across **three concrete engineering tracks** that together form a complete, end-to-end solution. Each track owns a clearly defined subsystem, delivers testable outputs, and integrates with the others through explicitly defined interfaces.

This structure is designed to:

- Enable parallel development  
- Prevent responsibility overlap  
- Maintain integration stability  
- Support incremental milestones  

---

## Overview of the Three Technical Tracks

The project is organised into the following tracks:

1. **Sensing & Data Acquisition** (ESP32 + Camera)  
2. **FPGA Node & Local Processing** (PYNQ / Jupyter / HDMI)  
3. **Backend, Database & User Interface** (Web Frontend)  

The **FPGA node (PYNQ-Z1)** is the primary system node as defined by the coursework specification.  
The **ESP32 and camera** together form the wand-side sensing subsystem.
The **Backend,Database&User interface** Allows the system to be usable and applicable

---

## Track 1 — Sensing & Data Acquisition (ESP32 + Camera)

### Scope

This track owns all wand-side sensing and observation, including both inertial sensing and vision-based tracking.

It is responsible for producing **clean, time-aligned, segmented raw data streams** for the FPGA node.

### Responsibilities

- IMU interfacing (MPU6050 via I²C)  
- Fixed-rate IMU sampling and timestamping  
- Gyroscope bias calibration at startup  
- Lightweight preprocessing (sanity checks, scaling if required)  
- Motion segmentation (gesture start / end detection)  
- Driving and controlling the wand marker (IR LED or visible LED)  
- Camera setup and calibration  
- Vision-based tracking of the wand marker (2D position extraction)  
- Synchronisation of camera data with motion segments  
- UART transmission of IMU data and segmentation events to the FPGA node  
- Power stability and basic hardware reliability  

### Explicit Non-Responsibilities

- Gesture or shape classification  
- Path interpretation or semantic decision making  
- FPGA hardware design or acceleration  
- Cloud communication or persistence  
- User-facing interfaces  

### Data Outputs (to FPGA Node)

- **IMU_SAMPLE**  
- (seq, dt/timestamp, ax, ay, az, gx, gy, gz)

- **SEG_START / SEG_END** events  

- **2D_POSITION** samples  
- Per camera frame during active segments  

- **CONFIG** packet  
- Sensor ranges  
- Sample rates  
- Device ID  

### Deliverables

- Stable ESP32 firmware producing segmented IMU data  
- Camera tracking module producing reliable 2D coordinates  
- Defined and documented UART data protocol  
- Hardware bring-up, calibration, and validation notes  

### Success Criterion

Moving the wand produces **consistent, segmented IMU data** and a **stable 2D positional trace** that is correctly received by the FPGA node.

---

## Track 2 — FPGA Node & Local Processing (PYNQ / Jupyter / HDMI)

### Scope

This track owns all node-side intelligence, local processing, and real-time presentation.

The **PYNQ-Z1** acts as the local decision-making node, performing processing independently of the backend.

### Responsibilities

#### Node-Side Software (PS)

- UART reception and buffering of IMU and camera data  
- Synchronisation of inertial and visual data streams  
- Software baseline processing pipeline  
- 2D path reconstruction and normalisation  
- Local gesture / shape recognition  
- Minimum demo: **line** and **circle**  
- HDMI output  
- Real-time path drawing  
- Classification result display  
- Local configuration handling  

#### FPGA Hardware (PL)

- Deterministic signal processing on IMU data:
- Filtering  
- Energy accumulation  
- Peak detection  
- Segment-level feature extraction  
- AXI-based interfaces (DMA / streaming)  
- Fixed-point optimisation where appropriate  
- Performance and resource utilisation measurement  

### Explicit Non-Responsibilities

- Raw sensor acquisition  
- Camera calibration or vision tracking  
- Cloud session management  
- Web or user interface development  

### Deliverables

- Working local classification pipeline  
- HDMI demo showing reconstructed path and classification  
- FPGA design (if implemented) with measured benefit  
- Software vs hardware performance comparison  
- Reproducible Jupyter notebooks / scripts  

### Success Criterion

The FPGA node can locally **reconstruct a 2D drawing**, **classify a basic shape** (e.g. line or circle), and **display the result in real time via HDMI**.

---

## Track 3 — Backend, Database & User Interface

### Scope

This track owns all server-side logic and user-facing interfaces, including multi-node coordination and interactive presentation.

It provides the system-level experience beyond a single FPGA node.

### Responsibilities

- Backend API or WebSocket server  
- Multi-node session management  
- Receiving classification results or events from nodes  
- Sending configuration or mode updates to nodes  
- Database schema and persistence  
- System-level logging for testing and evaluation  
- User-facing interface  
- Web dashboard or web-based game  
- Visualisation of node outputs and system state  
- Deployment (local or EC2)  

### Explicit Non-Responsibilities

- Sensor handling  
- Vision or inertial processing  
- FPGA or hardware design  
- Real-time HDMI rendering  

### Deliverables

- Backend server supporting multiple FPGA nodes  
- Reliable bidirectional communication  
- Database storing events and system state  
- User-facing web interface demonstrating interaction  
- Deployment and usage documentation  

### Success Criterion

Multiple FPGA nodes can connect to the backend, affect **shared system state**, and interact through a **user-facing interface**.

---

## Cross-Track Integration Rules

- All interfaces (UART packets, message schemas, APIs) **must be documented**  
- No track may change an interface without coordination  
- End-to-end demos take priority over internal optimisation  
- Software baselines must exist before FPGA acceleration  
- Camera-derived 2D position is the **authoritative spatial reference**  

---

## Project Lead & Integration Role

One member acts as **Project Lead / System Integrator**.

### Responsibilities

- Maintain architectural consistency across tracks  
- Approve interface and scope changes  
- Run milestone reviews and accept demos  
- Coordinate merges and feature freezes  

The Project Lead may actively contribute to one technical track while retaining **overall integration authority**.

---

## Definition of Done (All Tracks)

A task is considered complete only when:

- The functionality runs as intended  
- The output can be demonstrated  
- The change integrates cleanly with other tracks  
- Relevant documentation is updated  


