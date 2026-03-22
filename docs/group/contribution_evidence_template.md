# Contribution Evidence Template

This document is a **fact-control worksheet** for writing the project
management and contribution sections of the final report.

Its purpose is to help separate:

- original planned responsibility
- confirmed contributions to the **final presented model**
- exploratory or partial work that was **not adopted**
- contributions that are still **awaiting confirmation**

This template should be completed before writing any evaluative prose.

---

## Core Attribution Principles

- Attribute only what can be supported by evidence
- Treat the **final presented model** as the main reference point
- Acknowledge exploratory work without overstating its role in the final system
- If contribution status is unclear, mark it as **pending confirmation**
- Avoid converting absence of evidence into a stronger claim than the evidence
  supports

Recommended evidence sources:

- repository commits or authored files
- dated deliverables or shared artefacts
- meeting records
- task assignment notes
- design discussions with follow-up implementation
- demo evidence
- integration and test records

Where appropriate, record **shared final-phase delivery** separately from
primary implementation ownership. This is useful when:

- one person or subgroup owned major parts of the final adopted architecture
- other contributors were nevertheless highly committed and materially involved
  in final testing, debugging, rapid iteration, or integration work

---

## 1. Member-Level Evidence Matrix

Use this table to prepare a conservative contribution record for each member.

| Member | Planned responsibility | Confirmed contribution to final presented model | Exploratory / partial / non-adopted work | Evidence source | Confidence status |
| --- | --- | --- | --- | --- | --- |
| Yi | Early project setup and planning, wand-side track ownership at project start, and later system integration / delivery leadership | Primary implemented owner of major parts of the final presented system, including the adopted fallback FPGA centroid design path, PS/runtime code, UDP sender path, WandBrain UDP ingest/parse/runtime path, final integrated backend wrapper, database integration, live web console, final end-to-end integration, and shared final report writing / demo-video production with Wells and Mingze | Early exploratory work also exists on the branch history, including pre-final ESP32/IMU proof-of-concept work from the earlier architecture stage | `develop` branch history (treated as Yi’s delivery branch for report-preparation purposes), current adopted file structure under `FPGA/` and `software/`, the final demonstrated system record, and direct project clarification on final report/video collaboration | Confirmed |
| Wells | FPGA track ownership, including PL architecture, PS bindings, and general Zynq-board development | Active contribution to the final pre-demonstration integration, testing, debugging, and rapid development phase of the adopted system, together with shared final report writing and demo-video production | A more ambitious FPGA image-processing design path, including custom HDL and hardware export artefacts, which did not become the final adopted centroid-based PL implementation, plus later documentation/presentation work on that FPGA path | Wells branch commits (`6533bcc`, `19c422f`), `wells_report` branch commits (`83019cb`, `9412af4`, `0808de3`, `4edeeff`, `8882966`, `0dff49a`, `7acea3b`), project chronology, and final integration record | Confirmed |
| Ellie | Backend track ownership, including website, API-facing backend work, and database-related development | Early backend MVP contribution, including a demo website, basic database layer, and API/web updates aligned with the MVP backend contract; this should be recognised as meaningful early backend work that informed the final system direction | The visible branch implementation appears to be an MVP-stage backend/web/database path rather than the final full adopted backend stack used in the final presented model | Ellie branch commits (`58feeb7`, `d4ec96d`, `33bfc65`), authored frontend/database/API files, and comparison with the later adopted backend | Confirmed |
| Ananya | Wand-side / sensing-side work associated with the early wand track | No confirmed adopted contribution to the final presented LED-wand + camera + PYNQ model has been established from the current GitHub evidence alone | A concrete ESP32-based exploratory wand path, including IMU-driven wand firmware, UART text protocol notes, pin mapping, IR LED and motor test sketches, and an ESP32 wand controller README | Ananya branch commits (`a709c7a`, `db8d658`, `38dae81`, `b139dfd`, `59f059e`, `2fceea9`, `0ac3175`) and the authored files under `docs/group/docs/weekly_task/` | Confirmed |
| Mingze | FPGA node and local processing track, including node-side processing, local visual output, and associated hardware-side support | Final-system-relevant hardware and validation support, including camera hardware notes, camera-mount CAD assets, LED-wand CAD/schematic artefacts, BOM and hardware-summary documentation, auxiliary PYNQ-side test scripts, active contribution to the final pre-demonstration integration/testing push, and shared final report writing / demo-video production | Current GitHub evidence does not by itself show primary ownership of the final adopted PS/runtime path or the final centroid-based PL implementation | `feat/hardware` branch commits `6dcf9b2`, `4e8db4c`, and `b5a205f` by `MSB_233`, added files under `hardware/camera/`, `hardware/wand/current_led_wand/`, `hardware/`, and `FPGA/runtime/test/`, plus the final integration record | Confirmed |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] | [Confirmed / partial / pending confirmation] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] | [Confirmed / partial / pending confirmation] |

---

## 2. Final Presented Model Ownership Matrix

Use this table for the work that directly underpinned the final demonstrated
system.

| Final system area | Primary implemented owner | Supporting contributors | Evidence basis | Notes for report wording |
| --- | --- | --- | --- | --- |
| Adopted fallback FPGA PL design (`frame_centroid`, centroid-based block design, exported bit/hwh path) | Yi | Wells, Mingze supported final testing and integration as applicable | Current adopted FPGA artefacts in `FPGA/designs/centroid_pipeline/used_version/` and report-preparation assumption that `develop` is Yi’s delivery branch | This can be written as primary ownership of the adopted fallback PL path, while still acknowledging collaborative late-stage validation |
| PYNQ PS/runtime path, including centroid readout, local sketch logic, HTTP node control, and UDP sender | Yi | Wells, Mingze supported final testing and rapid iteration in the last phase as applicable | `FPGA/runtime/pynq_wand_brain_demo.py`, `FPGA/runtime/pynq_udp_bridge.py`, and associated develop-branch history | This is part of the final adopted node-side implementation, not just documentation |
| WandBrain UDP ingest, packet parser, live runtime, and scoring pipeline | Yi | [Insert if later confirmed] | Adopted backend files under `software/cloud/backend/versions/brain_v2_scoring/src/brain/` and develop-branch delivery history | Safer wording is that Yi implemented the final adopted WandBrain path while earlier MVP work from others can be acknowledged separately |
| Final integrated backend wrapper, database integration, and live web console used in the presented system | Yi | Ellie contributed earlier backend MVP foundation; Wells and Mingze supported final-phase testing/integration as applicable | `software/cloud/main.py`, `software/cloud/node_control.py`, `software/cloud/database/*`, `software/cloud/frontend/index.html`, and current develop-branch state | This should be phrased to distinguish final adopted implementation ownership from earlier MVP-stage backend work |
| Integration and testing of the final presented system | Yi | Wells, Mingze | Final pre-demo project record, direct collaboration history, and final demonstrated system | Primary implementation ownership and final validation effort should be described separately: the core adopted architecture may be attributed to its implementer, while the final rapid debugging and testing phase should be described as collaborative |
| Final report writing and demo video production | Shared by Yi, Wells, and Mingze | [Insert if later confirmed] | Direct project clarification on final report/video collaboration, later documentation/media preparation record, and final submission artefacts | This should be presented as shared final-phase documentation and presentation work, separate from primary implementation ownership of the final adopted technical architecture |
| Early backend MVP: frontend, database scaffold, and core web API path | Ellie | [Insert if later confirmed] | Ellie branch commits and authored files in `cloud/frontend`, `cloud/database`, and backend API updates | This should be described as early backend MVP work. It is safer to say it informed or established an MVP-stage path than to present it as the complete final backend used in the final demonstrated system |
| Physical sensing setup support: camera selection notes, camera-mount CAD, LED-wand CAD/schematic assets, BOM/hardware-summary documentation, and auxiliary node-side bring-up tests | Mingze | Yi and Wells contributed to final integration/testing around the same physical setup as applicable | `feat/hardware` branch commits `6dcf9b2`, `4e8db4c`, and `b5a205f`, plus artefacts under `hardware/camera/`, `hardware/wand/current_led_wand/`, `hardware/`, and `FPGA/runtime/test/` | Safe wording is that Mingze contributed final-system-relevant hardware documentation, CAD assets, BOM/design packaging, and auxiliary verification scripts supporting the adopted physical setup, while primary ownership of the final runtime remained elsewhere |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |

Suggested system areas:

- fallback PL design
- PS/runtime code
- UDP sender
- UDP receiver and parser
- WandBrain runtime
- backend wrapper
- database layer
- frontend / web interface
- physical hardware support
- integration and testing

Use the `Supporting contributors` column to record people who contributed
substantially to validation, fast iteration, or final integration, even where
primary implementation ownership remained elsewhere.

---

## 3. Non-Adopted or Exploratory Work Log

Use this table to acknowledge work that existed but was not part of the final
presented model.

| Work item | Contributor(s) | Purpose at the time | Why it was not adopted in the final model | Conservative wording for report |
| --- | --- | --- | --- | --- |
| Advanced FPGA image-processing PL path (`imageProcessTop`, `imageControl`, `conv`, `lineBuffer`, plus associated exported hardware files) | Wells | To pursue a richer hardware processing pipeline on the FPGA path | The branch evidence indicates a more complex image-processing implementation route than the simpler centroid-based fallback design ultimately adopted for final integrated delivery | `Wells contributed substantial FPGA architectural work, including a more advanced image-processing PL path. However, this branch of work did not become the main basis of the final adopted centroid-based FPGA implementation.` |
| Early backend MVP implementation on Ellie branch (`cloud/frontend/index.html`, `cloud/database/*`, and MVP API/server updates) | Ellie | To provide an early usable website, database persistence path, and basic backend API support for the MVP system | The final backend and live console were later substantially extended and reorganised, so the visible branch work is best described as MVP-stage or early-foundation backend work rather than the complete final adopted backend implementation | `Ellie contributed an early backend MVP, including a demo website, database code, and basic API-facing updates. This work formed an early backend path, but the final deployed backend used for the presented system was later extended and reworked beyond this MVP stage.` |
| ESP32-based wand firmware and support material (`wand_esp32.ino`, `esp32_wand_controller.ino`, `uart_format.md`, `pin_mapping.md`, `ir_led_test.ino`, `motor_test.ino`, `readmeforwand.md`) | Ananya | To support an ESP32/IMU-based wand concept with UART, IR LED output, and haptic feedback | The final presented system did not adopt the ESP32-based wand architecture and instead used the later LED-wand + camera + PYNQ path | `Ananya contributed a concrete exploratory ESP32 wand path, including firmware, protocol notes, and hardware guidance. However, this work was not part of the final adopted system because the final presented model did not use the ESP32-based wand architecture.` |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |

Examples of neutral phrasing:

- `an exploratory implementation was produced but not incorporated into the final integrated system`
- `this work informed early planning but was not part of the final presented model`
- `the artefact existed at MVP stage but did not form the main basis of the final backend`
- `the contribution remained partial and was not adopted into the final delivery path`

---

## 4. Unverified or Pending-Confirmation Contributions

Use this section for areas where attribution is not yet certain enough to state
as fact in the report.

| Member | Claimed or suspected contribution | Current evidence available | What still needs confirmation | Report status |
| --- | --- | --- | --- | --- |
| Apshara | Early involvement in the wand-side group and possible later involvement around the backend-side group after role movement in project discussions | Current evidence is limited to planning/role-allocation records and project chronology notes; no visible authored GitHub branch or commit record has been identified in the accessible repository | Whether Apshara produced technical artefacts, implementation work, testing support, documentation, or coordination work that should be acknowledged in the final report | Mention cautiously only as planned role / pending confirmation |
| Seth | Planned involvement in the backend group | Current evidence is limited to planned role references in project documentation; no visible authored GitHub branch or commit record has been identified in the accessible repository | Whether Seth produced any technical, documentation, coordination, or testing contribution outside the visible repository record | Do not state as delivered contribution until confirmed |
| [Insert] | [Insert] | [Insert] | [Insert] | [Do not state yet / mention cautiously / ready to include] |

---

## 5. Critical-Path Ownership Summary

Use this section to isolate the work that most affected final delivery.

| Critical-path area | Why it was critical | Final implemented owner | Recovery or intervention required | Evidence source |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |

### 5.1 Late-Stage Integration and Recovery Notes

Use this subsection to record cases where the final delivery phase became a
short, high-intensity collaborative effort.

| Final integration activity | Primary owner | Other committed contributors | Nature of collaboration | Evidence source |
| --- | --- | --- | --- | --- |
| Final pre-demonstration system bring-up and validation | Yi | Wells, Mingze | Rapid testing, debugging, joint iteration, and system bring-up | Project chronology and direct final-phase collaboration record |
| Final report writing and demo video production | Shared by Yi, Wells, and Mingze | [Insert if later confirmed] | Shared writing, review, asset preparation, and demo-video production | Direct project clarification and final report/video preparation record |
| [Insert] | [Insert] | [Insert] | [Rapid testing / debugging / joint iteration / system bring-up] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Rapid testing / debugging / joint iteration / system bring-up] | [Insert] |

This helps the report reflect two facts at the same time:

- who owned the core implementation of the final adopted system
- who was actively committed and involved in the final recovery and validation
  effort

---

## 6. Safe Report-Writing Rules

When converting this worksheet into report prose:

- write `planned responsibility` separately from `actual delivery`
- write `final presented model` separately from `non-adopted work`
- write `confirmed contribution` separately from `pending confirmation`
- focus on delivery impact, coordination burden, and risk response
- avoid emotional wording and avoid attributing motive

Prefer wording such as:

- `was originally assigned responsibility for`
- `contributed to an early MVP-stage implementation`
- `did not form part of the final adopted system`
- `the final implementation was delivered by`
- `ownership became concentrated around`
- `direct intervention was required to protect delivery`
- `the final integration and testing phase was completed collaboratively`
- `substantial final-phase effort was shared across rapid debugging and validation`
- `primary implementation ownership remained with [role/member], while final
  recovery and testing were supported by [role/member]`

Avoid wording such as:

- `did nothing`
- `failed completely`
- `refused to help`
- `unfair`
- `I had to do everything`

---

## 7. Pre-Writing Checklist

Before writing the final report section, confirm:

- each member’s planned role is documented
- each final-system claim has evidence
- exploratory work is acknowledged separately from adopted work
- unverified contributions are not overstated
- critical-path ownership is clearly identified
- the language remains factual, conservative, and professional
