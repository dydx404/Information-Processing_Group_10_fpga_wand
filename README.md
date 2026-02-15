# FPGA-Wand  
**Distributed Gesture Recognition Using ESP32, FPGA, and Cloud Backend**

**Information Processing — Group 10 Project**

---

## Overview

FPGA-Wand is a **multi-node, edge-to-cloud gesture recognition system** developed as part of the *Information Processing* coursework.

Each node (referred to as a *wand*) captures motion data using onboard sensors, performs **local processing on an FPGA-based node**, and optionally communicates with a **cloud backend** to enable real-time, collaborative, gesture-based interaction.

The project demonstrates a complete, end-to-end system spanning:

- Embedded sensing  
- FPGA-accelerated signal processing  
- Networked coordination and persistence  

A strong emphasis is placed on **clear interfaces**, **layer separation**, and **system-level correctness** over isolated optimisation.

---

## System Architecture

The system is organised as a layered architecture, with each layer having a clearly defined responsibility and interface.

### 1. ESP32 Wand (Sensing Layer)

Responsibilities:
- Inertial sensing using an IMU
- vision-based tracking using a camera
- Motion segmentation and basic preprocessing
- UART transmission of time-aligned sensor data

This layer is responsible only for **data acquisition and conditioning**, not interpretation.

---

### 2. FPGA / Node Processing (Edge Intelligence)

Runs on a **PYNQ-Z1 FPGA SoC**.

Responsibilities:
- Receiving sensor data from the ESP32 wand
- Local signal processing and feature extraction
- 2D motion path reconstruction
- Classification of basic gestures (e.g. line, circle)
- Real-time visual feedback via HDMI

This layer performs **deterministic, low-latency processing**, with selected components accelerated in FPGA fabric where appropriate.

---

### 3. Cloud Backend (Coordination Layer)

Responsibilities:
- Session and state management
- Multi-node coordination
- Configuration and event handling
- Optional game logic or interactive behaviour

---

### 4. Database (Persistence Layer)

Responsibilities:
- Storage of system state
- Logging for testing and evaluation
- Support for replay, debugging, and offline analysis

---

Architecture diagrams, interface definitions, and design decisions are documented in the `docs/` directory.

---

## Repository Structure

```text
wand/        ESP32 firmware, FPGA designs, and node-side software
cloud/       Backend server, database, and deployment scripts
protocol/    Message schemas and communication specifications
docs/        Architecture diagrams, testing notes, and report material
tools/       Development, debugging, and testing utilities
Repository Conventions
protocol/ is the single source of truth for all inter-module interfaces
```

Each directory corresponds to a clearly owned technical subsystem

Cross-module changes must be coordinated and reviewed

## Development Workflow
- All development is carried out on feature branches

- main is kept stable and demo-ready at all times

- Changes are merged via Pull Requests

- Interfaces must not be modified without cross-track agreement

- Contribution rules are defined in CONTRIBUTING.md

End-to-end functionality takes priority over internal optimisation

## Requirements
### Hardware

ESP32-based development board

FPGA SoC board (e.g. PYNQ-Z1)

Optional camera for vision-based tracking

### Software
Python 3.10 or newer

Vivado (for FPGA development and synthesis)

PYNQ environment (Jupyter-based control and drivers)

Cloud (Optional)
AWS account

EC2 instance for backend deployment

Project Goals
Minimum Successful Demonstration
The minimum viable system demonstrates:

A wand producing segmented motion data

An FPGA node reconstructing and classifying a gesture locally

Real-time visual feedback displayed via HDMI

## Extended Functionality
Optional extensions include:

Multi-node interaction

Cloud-backed coordination

Web-based visualisation or game logic

Status
This project is under active development as part of the Information Processing coursework.

Milestones, demonstrations, and integration status are tracked in the docs/ directory.