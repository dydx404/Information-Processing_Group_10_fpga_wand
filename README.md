# FPGA-Wand  
**Distributed Point-Tracking and Shape Recognition System**  
*Information Processing — Group 10*

---

## Overview

FPGA-Wand is a **distributed, edge-to-cloud interactive system** for real-time motion tracking and shape recognition.

Each *wand* captures motion using infrared point tracking and inertial sensing, transmits time-aligned data to an FPGA-based edge node, and reconstructs a 2D trajectory in real time. The reconstructed path is then **classified and scored** against predefined reference shapes, with immediate visual feedback.

Rather than treating “gesture recognition” as a black box, the project deliberately separates:

- sensing  
- reconstruction  
- classification  
- coordination  

Each stage has a **clearly defined responsibility and interface**, prioritising system-level correctness, determinism, and debuggability over opaque optimisation.

---

## Key Design Principles

- **Clear layer separation** — no hidden cross-dependencies  
- **Explicit protocols** — all inter-module communication is documented  
- **Deterministic edge processing** — low latency, predictable behaviour  
- **Extensible architecture** — new shapes, nodes, or behaviours can be added without refactoring the core  

---

## System Architecture

The system is organised as a four-layer architecture.

### 1. ESP32 Wand — Sensing Layer

Responsibilities:
- Infrared point detection (camera-based)
- Inertial sensing using an IMU
- Basic motion segmentation and filtering
- Timestamping and packetisation
- UART transmission to the FPGA node

This layer **only acquires and conditions data**.  
It performs **no interpretation or classification**.

---

### 2. FPGA Node — Edge Intelligence Layer

Runs on a **PYNQ-Z1 FPGA SoC**.

Responsibilities:
- Receiving sensor packets from the ESP32
- Time alignment and buffering
- 2D trajectory reconstruction
- Shape normalisation and comparison
- Scoring against predefined reference shapes
- Real-time HDMI visual output

Processing is designed to be **deterministic and low-latency**, with FPGA fabric used where acceleration is beneficial and ARM cores handling control logic.

This layer is the **authoritative decision-making core** of the system.

---

### 3. Cloud Backend — Coordination Layer (Optional)

Responsibilities:
- Session and node management
- Multi-wand coordination (e.g. competition or collaboration)
- Event handling and configuration distribution
- Optional game logic or interaction rules

The system remains fully functional **without the cloud**.  
Cloud services are additive, not required.

---

### 4. Database — Persistence Layer

Responsibilities:
- Logging trajectories, scores, and events
- Supporting replay and offline analysis
- Debugging and evaluation

This layer exists to support development, testing, and demonstrations, not real-time control.

---

## Repository Structure

```text
wand/        ESP32 firmware, FPGA designs, and node-side software
cloud/       Backend server, database schema, and deployment scripts
protocol/    Message formats and communication specifications
docs/        Architecture diagrams, reports, and testing notes
tools/       Development, debugging, and test utilities
Repository Conventions

protocol/ is the single source of truth for all interfaces

Each directory corresponds to a clearly owned subsystem

Cross-module changes must be coordinated

Interfaces may not be changed unilaterally

Development Workflow

All development occurs on feature branches

main is kept stable and demo-ready

Changes are merged via Pull Requests

Interface changes require cross-track agreement

End-to-end functionality takes priority over micro-optimisation

Contribution rules are defined in CONTRIBUTING.md.

Requirements
Hardware

ESP32-based development board

FPGA SoC board (e.g. PYNQ-Z1)

Infrared LED and camera module

Software

Python 3.10 or newer

Vivado (for FPGA synthesis)

PYNQ environment (Jupyter-based control and drivers)

Optional Cloud

AWS account

EC2 instance for backend deployment

Project Goals
Minimum Viable Demonstration

The minimum successful system demonstrates:

A wand producing segmented, timestamped motion data

An FPGA node reconstructing a 2D trajectory

Local classification and scoring against a reference shape

Real-time HDMI visual feedback

No cloud dependency is required for the MVP.

Extended Functionality

Optional extensions include:

Multi-node competitive or collaborative modes

Cloud-coordinated sessions

Web-based visualisation and replay

Expanded shape libraries and scoring rules

Status

This project is under active development as part of the Information Processing coursework.

Milestones, integration status, and design decisions are documented in the docs/ directory.

FPGA-Wand emphasises clarity, determinism, and system-level thinking — treating hardware, software, and communication as one coherent machine rather than isolated components.