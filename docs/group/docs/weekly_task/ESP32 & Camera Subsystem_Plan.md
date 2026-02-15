# Week 1 Tasks — ESP32 & Camera Subsystem  
**Project:** FPGA-Wand — Information Processing  
**Milestone:** Milestone 1 — Sensor-to-Node Data Path  
**Deadline:** 22 Feb

This document defines the **Week 1 responsibilities and deliverables for the ESP32 and camera subsystem only**.

The goal of Week 1 is to establish a **reliable, testable data source** that feeds motion or visual information into the FPGA node. Gesture recognition accuracy is *not* a requirement at this stage; correctness of data flow and segmentation is.

If a deliverable is not committed to the repository, the task is considered **incomplete**.

---

## Subsystem Ownership — ESP32 & Camera

**Members**
- yi  
- Ananya  
- Apshara  

This subgroup owns **all sensor-side data generation and transmission**, including optional camera-based tracking.

---

## Scope

This subsystem is responsible for:

- Initialising and running the ESP32 firmware
- Acquiring motion or visual tracking data
- Performing **basic segmentation** (start / stop of motion)
- Transmitting framed, time-aligned data to the FPGA node
- Providing simple local feedback (LED / buzzer) for system state

No classification, reconstruction, or cloud interaction is required in Week 1.

---

## Week 1 Objectives

By the end of Week 1, the ESP32 must function as a **deterministic sensor node** that:

- Produces repeatable motion or tracking data
- Clearly marks the beginning and end of a gesture segment
- Streams data reliably to the FPGA node over UART

---

## Data Sources (Choose at Least One)

At least one of the following data sources must be implemented:

### Option A — IMU-Based Motion Data
- Accelerometer and/or gyroscope readings
- Fixed sampling rate
- Raw or lightly filtered values

### Option B — Camera-Based Tracking
- IR or optical camera attached to ESP32
- Extraction of 2D point(s) or centroid
- Frame-to-frame position tracking
- Output reduced to low-bandwidth numerical data

Synthetic or replayed data is acceptable **only for initial bring-up**, not for the final Week 1 demo.

---

## Week 1 Tasks

### Firmware & Environment
- Set up ESP32 development environment
- Flash and verify firmware on hardware
- Document flashing and recovery procedure

### Data Acquisition
- Acquire sensor or camera data at a fixed rate
- Timestamp or sequence-number samples
- Ensure numerical stability and repeatability

### Motion Segmentation
- Detect gesture start and end
- Implement explicit segment markers
- Ignore idle/noise regions

### UART Communication
- Define a clear UART frame format
- Transmit framed data to FPGA node
- Handle framing errors gracefully

### Local Feedback
- LED or buzzer indicates:
  - System active
  - Segment start / end
  - Command received from FPGA node

---

## Week 1 Deliverables

By the deadline, the following must be demonstrable:

- ESP32 continuously streams framed data over UART
- Gesture segments have visible start/end markers
- FPGA node can receive and parse the data stream
- Local feedback responds to at least one external command

---

## Required Repository Output

The following **must be committed**:

- ESP32 firmware source code
- UART frame format specification
- Wiring diagram or pin mapping
- Testing instructions

### Required Documentation
```text
docs/esp32/
├── README.md          Build, flash, and run instructions
├── protocol.md        UART frame format and segmentation markers
└── wiring.md          ESP32 ↔ sensors / camera wiring
