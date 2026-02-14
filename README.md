# Information-Processing_Group_10_fpga_wand
Information Processing — Group 10 Project

# FPGA-Wand
**Distributed Gesture Recognition Using ESP32, FPGA, and Cloud Backend**

FPGA-Wand is a multi-node IoT system developed for the *Information Processing* group project. Each node (“wand”) captures motion data, performs local processing, and communicates with a cloud server to enable real-time, collaborative, gesture-based interaction.

The project combines embedded sensing, FPGA-accelerated processing, and cloud-based coordination to demonstrate a complete edge-to-cloud system.

---

## System Architecture

The system is composed of four main layers:

- **ESP32 Wand**  
  Motion sensing and low-level data acquisition.

- **FPGA / Node Processing**  
  Local signal processing, feature extraction, and optional hardware acceleration (Vivado + PYNQ).

- **Cloud Backend (EC2)**  
  Session management, coordination between nodes, and event handling.

- **Database**  
  Storage of system state, logs, and evaluation data.

Architecture diagrams and design decisions are documented in `docs/`.

---

## Repository Structure

```text
wand/        ESP32 firmware, FPGA designs, and node software
cloud/       Backend server, database, and deployment scripts
protocol/    Message schemas and examples (single source of truth)
docs/        Architecture, testing, and report materials
tools/       Development and testing utilities
```

## Development Workflow

All work is done on feature branches.

main is kept stable and demo-ready.

Changes are merged via Pull Requests.

Contribution rules are defined in CONTRIBUTING.md.

## Requirements

ESP32-based development board

FPGA SoC board (e.g. PYNQ-Z1)

Python 3.10+

Vivado (for FPGA development)

AWS account (for cloud deployment)

