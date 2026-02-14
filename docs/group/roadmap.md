# Project Timeline and Milestone Plan  
**FPGA-Wand — Information Processing Group Project**

**Start date:** 14 Feb  
**Submission deadline:** 12 Mar  

This document defines the planned timeline, regular meeting structure,
and task-based milestones for the FPGA-Wand project.  
The goal is to ensure that core functionality is delivered early, with
progressive extensions layered on top while preserving redundancy and
integration time.

---

## Meeting Structure

- **Weekly group meetings:** Every weekend
- **Purpose of meetings:**
  - Demonstrate working functionality (not slides)
  - Review completed tasks against milestones
  - Decide scope adjustments if needed
- **Expectation:** Each meeting must include a **live demo**, even if minimal

Meetings are milestone-driven rather than discussion-driven.

---

## Milestone Philosophy

The project is structured as a sequence of **incremental demos**:

1. A **minimum viable demo** that satisfies coursework requirements
2. Progressive extensions that add capability and “X-factor”
3. Optional stretch goals that are only attempted if the system is stable

At every stage, the system must remain runnable end-to-end.

---

## Milestone 1 — End-to-End Connectivity (by 21 Feb)

### Objective
Demonstrate a complete data loop between nodes and cloud.

### Required Demo
- At least **two nodes** connect to the cloud server
- Nodes send events or data to the server
- Server sends configuration or state updates back
- Nodes respond to server messages (even trivially)

### Notes
- Gesture recognition may be stubbed
- FPGA acceleration is **not required** at this stage
- Reliability matters more than sophistication

This milestone de-risks the entire project.

---

## Milestone 2 — Minimum Gesture Demo: Circle Drawing (by 28 Feb)

### Objective
Demonstrate meaningful **local processing** on the node.

### Required Demo
- Wand motion input produces a detectable trajectory
- Local processing classifies a **circle gesture**
- Result is sent to the cloud
- Cloud updates shared state and broadcasts feedback
- Nodes react to the updated state

This demo satisfies the **minimum functional requirements** of the coursework.

---

## Milestone 3 — Advanced Gestures (“Special Spells”) (by 5 Mar)

### Objective
Extend the system with richer interaction while preserving stability.

### Example Features (choose a subset)
- Multiple gesture types (e.g. line, triangle, figure-eight)
- Gesture sequences (“spell casting”)
- Difficulty or threshold changes pushed from the cloud
- Different behaviour per node based on server state

### Notes
- Gesture logic may remain software-based
- FPGA acceleration may be introduced as an optimisation

This milestone contributes directly to the **X-factor** component.

---

## Milestone 4 — Optional Sketching / Image Generation (Stretch Goal)

### Objective
Demonstrate creative or cross-modal system behaviour.

### Example Features
- Drawing trajectories reconstructed into images
- Server-side image generation based on wand input
- Shared “canvas” across nodes
- Visual feedback loop (gesture → image → node update)

### Notes
- This milestone is **optional**
- Only attempted if earlier milestones are stable
- Failure to complete this does **not** jeopardise core marks

---

## Freeze and Integration Period (6–8 Mar)

### Rules
- No new features after 6 Mar
- Bug fixes and reliability improvements only
- Documentation updated to reflect actual behaviour

### Deliverables
- Stable demo flow
- Testing evidence
- Performance and resource metrics
- Final architecture diagrams

---

## Final Phase — Report, Video, and Oral Preparation (9–12 Mar)

### Focus
- Clear explanation of:
  - System architecture
  - Design decisions and trade-offs
  - Performance metrics
  - Testing methodology
- Demo rehearsed and repeatable
- All members prepared to explain their contributions

---

## Summary Timeline

- **14 Feb:** Setup complete  
- **21 Feb:** End-to-end system demo  
- **28 Feb:** Circle drawing demo (minimum requirement)  
- **5 Mar:** Advanced gestures / spells  
- **6 Mar:** Feature freeze  
- **12 Mar:** Submission  

---

## Guiding Principle

A simple system that works reliably scores higher than a complex system
that is incomplete.

Progressive demos ensure that functionality is never lost while ambition
is explored.
