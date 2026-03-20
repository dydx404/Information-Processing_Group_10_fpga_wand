# Member Contribution Notes

This document collects **report-safe, evidence-based attribution notes** for
individual members.

It is intended to support the final report by separating:

- planned responsibility
- confirmed contribution to the **final presented model**
- exploratory or non-adopted work
- wording that remains professional, conservative, and defensible

These notes should be updated only when there is a clear evidence basis for the
claim being added.

---

## Yi

### Planned responsibility

Yi appears in the project history both as the early organiser of the repository
and planning structure and as a technical contributor across the project’s
development.

The early branch and documentation history supports planned responsibility in
at least three areas:

- initial project setup and documentation
- early wand-side exploration
- system-level coordination and integration planning

For report-preparation purposes, the `develop` branch is being treated as Yi’s
delivery branch, following direct project clarification.

### Confirmed evidence

The current `develop` branch contains the adopted project structure and the
final documented implementation path. Its visible history also shows sustained
Yi-authored commits across:

- repository setup
- working agreement and milestone documents
- protocol and API definitions
- WandBrain MVP and later backend evolution
- testing scripts
- final repo restructuring and documentation of the delivered system

The authorship history on `develop` is dominated by Yi-associated identities:

- `Yi DONG <yd1723@ic.ac.uk>`
- `dydx404 <yd1723@ic.ac.uk>`
- `dydx <yd1723@ic.ac.uk>`

This makes it reasonable, for report purposes, to treat `develop` as the main
evidence base for Yi’s implemented contribution to the final adopted system.

### Relation to the final presented model

Under that evidence rule, the final presented model shows Yi as the primary
implemented owner of major parts of the adopted system, including:

- the adopted fallback FPGA PL design path
  - [`frame_centroid.v`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/FPGA/designs/centroid_pipeline/used_version/source/frame_centroid.v)
  - [`design_1_wrapper.tcl`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/FPGA/designs/centroid_pipeline/used_version/source/design_1_wrapper.tcl)
- the node-side PS/runtime and UDP sender path
  - [`pynq_wand_brain_demo.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/FPGA/runtime/pynq_wand_brain_demo.py)
  - [`pynq_udp_bridge.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/FPGA/runtime/pynq_udp_bridge.py)
- the final adopted WandBrain ingest/runtime path
  - [`server.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/backend/versions/brain_v2_scoring/src/brain/api/server.py)
  - [`parser.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/backend/versions/brain_v2_scoring/src/brain/ingest/parser.py)
  - [`udp_rx.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/backend/versions/brain_v2_scoring/src/brain/ingest/udp_rx.py)
- the final integrated backend wrapper, node-control layer, database
  integration, and live web console
  - [`main.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/main.py)
  - [`node_control.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/node_control.py)
  - [`models.py`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/database/models.py)
  - [`index.html`](/home/bensonyi/FPGA_wand/Information-Processing_Group_10_fpga_wand/software/cloud/frontend/index.html)

The evidence also supports substantial contribution to:

- protocol definition and documentation
- testing and smoke-test tooling
- final architecture, validation, and report-facing documentation

### Technical character of the contribution

The visible develop-branch record is not limited to one subsystem. It spans:

- project setup and management scaffolding
- hardware/software interface definition
- FPGA fallback implementation
- PYNQ runtime implementation
- UDP transmission protocol definition and sender path
- server-side receive/parse/runtime logic
- backend and database integration
- live frontend/dashboard development
- integration testing and final documentation

The conservative interpretation is therefore not merely that Yi contributed
heavily, but that Yi was the primary implemented owner of the final adopted
cross-subsystem delivery path.

### Relation to exploratory work

The branch history also contains earlier exploratory work, including
ESP32/IMU-based wand experimentation from a previous architectural stage.

That exploratory work should be acknowledged, but it should not be confused
with the final adopted architecture. The main report emphasis should remain on
the adopted LED-wand + camera + PYNQ + WandBrain system preserved on
`develop`.

### Final-phase collaboration

The current project record also indicates that the final pre-demonstration
phase involved shared rapid development, testing, and debugging with Wells and
Mingze.

The report should therefore distinguish between:

- Yi’s primary implementation ownership of major parts of the adopted system
- the collaborative nature of the final integration and testing push

### Report-safe interpretation

The safest interpretation for the final report is:

`Using the final adopted develop branch as the main evidence base, Yi was the
primary implemented owner of major parts of the final presented system. This
included the adopted fallback FPGA design path, the PYNQ PS/runtime and UDP
sender path, the final WandBrain ingest/runtime path, and the final integrated
backend, database, and live web interface used in the demonstration. Yi also
contributed substantially to project setup, interface definition, testing, and
documentation. The final pre-demonstration phase nevertheless remained
collaborative, with rapid testing, debugging, and integration work shared with
other committed contributors.`

### Additional management interpretation

If needed for the project-management section, the following wording is
defensible:

`The final adopted system shows a high degree of implementation concentration on
the develop branch, which functioned as the main delivery path for the
presented model. This concentration applied not only to a single subsystem but
to the interfaces between FPGA, node software, UDP communication, backend
runtime, persistence, and user-facing operation.`

### Cautions

- This interpretation relies on the explicit report-preparation assumption that
  `develop` should be treated as Yi’s delivery branch
- where early MVP work by other members exists, it should still be acknowledged
  separately rather than erased by later integration ownership
- final-phase collaborative testing and debugging should be preserved in the
  report so that implementation ownership does not obscure shared recovery
  effort

---

## Wells

### Planned responsibility

Wells was part of the FPGA workstream and was originally associated with the
high-responsibility section covering PL architecture, PS bindings, and general
Zynq/PYNQ-side development.

Because the FPGA path was a critical dependency for end-to-end integration,
this role carried substantial project-management weight.

### Confirmed evidence

The visible GitHub evidence shows two Wells-authored commits on the `Wells`
branch:

- `6533bcc` (`2026-02-22`): adds custom HDL files
  - `conv.v`
  - `imageControl.v`
  - `imageProcessTop.v`
  - `lineBuffer.v`
- `19c422f` (`2026-03-09`): adds or reorganises FPGA hardware artefacts
  including:
  - `design_1.bit`
  - `design_1.hwh`
  - `design_1.tcl`
  - the above HDL files under a hardware folder

This supports the claim that Wells contributed real FPGA development work and
did not remain at planning level only.

### Relation to the final presented model

The branch evidence indicates that Wells pursued a more ambitious FPGA
image-processing design path based around modules such as `imageProcessTop` and
`imageControl`.

This is technically meaningful work, but it is not the same path as the
simpler centroid-based fallback PL design adopted in the final presented model.

The conservative distinction is therefore:

- Wells contributed substantive FPGA architectural and implementation work
- the visible branch artefacts do not appear to be the direct basis of the
  final adopted centroid-based PL implementation

### Final-phase collaboration

According to the current project record, Wells remained committed through the
final phase and participated actively in the last rapid integration, testing,
debugging, and development push alongside Yi and Mingze.

This means the report should distinguish between:

- primary implementation ownership of the adopted FPGA path
- collaborative late-stage validation and recovery effort

### Report-safe interpretation

The safest interpretation for the final report is:

`Wells contributed substantial FPGA architectural work and remained committed
throughout the project. His branch evidence shows a more advanced
image-processing PL design path with custom HDL and hardware export artefacts.
However, this work did not become the main basis of the final adopted
centroid-based FPGA implementation. In the final pre-demonstration phase, Wells
also contributed actively to rapid testing, debugging, and integration work.`

### Additional management interpretation

If needed for the project-management section, the following point is defensible
when phrased carefully:

`The FPGA workstream represented the main critical-path risk. The visible branch
evidence suggests that a comparatively ambitious PL design path was pursued
before a lower-risk working MVP path had been secured, which increased
integration pressure later in the project.`

This should be presented as a project-management observation about technical
strategy and delivery sequencing, not as a personal accusation.

### Cautions

- GitHub evidence supports Wells’s FPGA branch work
- GitHub alone does not prove meeting attendance or all lab-based activity
- claims about final-phase collaboration should be supported by the project
  chronology and direct participant records when used in the report

---

## Ellie

### Planned responsibility

Ellie was part of the backend workstream and was originally associated with the
website, database, and system-level backend path.

This role covered the user-facing frontend as well as the persistence and API
support needed for the cloud side of the system.

### Confirmed evidence

The visible GitHub evidence shows three Ellie-authored commits on the `ellie`
branch:

- `58feeb7` (`2026-02-22`): `demo website`
  - creates `cloud/frontend/index.html`
- `d4ec96d` (`2026-03-02`): `updating database code`
  - adds `cloud/database/database.py`
  - adds `cloud/database/init_db.py`
  - adds `cloud/database/main.py`
  - adds `cloud/database/models.py`
  - updates backend API integration
- `33bfc65` (`2026-03-04`): `updates to api and web page`
  - updates backend API code
  - updates database main logic
  - updates frontend files

This supports the claim that Ellie contributed real backend MVP work across the
frontend, database, and API-facing backend path.

### Technical character of the visible branch work

The visible branch work is consistent with an early backend MVP rather than a
fully developed final production-style backend.

The evidence supports the following specific points:

- a demo website was implemented
- a database layer and `Attempt` model were introduced
- basic API/web integration was added
- the backend API path already aligned with the MVP `/api/v1/*` contract

In particular, the branch includes early implementations of endpoints and data
structures that align with the documented MVP API family, including:

- `/api/v1/health`
- `/api/v1/wands`
- `/api/v1/wand/{wand_id}`
- `/api/v1/attempt/latest`
- `/api/v1/attempt/{attempt_id}/image.png`
- database-backed `Attempt` persistence

### Relation to the final presented model

The safest interpretation is that Ellie’s work established or supported an
early backend MVP path, but that the final backend used in the demonstrated
system was later substantially extended and reworked.

This is important because the final adopted backend includes significantly more
than the MVP branch evidence alone, such as:

- the later WandBrain wrapper structure
- expanded live console behaviour
- node control
- leaderboards
- extended database-backed features
- the final deployed EC2-facing integrated backend

At the same time, the MVP branch should not be dismissed. It provides concrete
evidence of meaningful backend contribution at an earlier stage, particularly
for:

- frontend prototyping
- database scaffolding
- basic backend/API integration

### Report-safe interpretation

The safest interpretation for the final report is:

`Ellie contributed an early backend MVP, including a demo website, database
code, and basic API-facing backend updates. The visible branch evidence shows
meaningful work on frontend structure, persistence, and MVP web APIs. However,
the final deployed backend used for the presented system was later extended and
reworked beyond this MVP stage, so Ellie’s contribution is best described as an
early backend foundation rather than the complete final backend implementation.`

### Additional management interpretation

If needed for the project-management section, the following wording is
defensible:

`The backend workstream did produce visible MVP-stage artefacts, particularly in
the form of website, database, and basic API work. However, the final presented
backend required further extension and integration before it matched the scope
of the adopted system.`

### Cautions

- GitHub evidence clearly supports Ellie’s early backend MVP contribution
- GitHub alone does not prove the full extent of later discussion or support
  activity outside the repository
- the safest distinction is between `early backend MVP work` and `final adopted
  backend ownership`, rather than treating them as identical

---

## Ananya

### Planned responsibility

Ananya was associated with the wand-side track during the earlier planning
phase, when the project still included an ESP32-based wand concept.

This places her planned responsibility within the sensing / wand-side area
rather than the final camera + PYNQ processing path that was eventually
adopted.

### Confirmed evidence

The visible GitHub evidence shows multiple Ananya-authored commits on the
`ananya` branch:

- `a709c7a` (`2026-02-18`): `Create wand_esp32.ino`
- `db8d658` (`2026-02-18`): `uart text protocol`
- `38dae81` (`2026-02-18`): `Add wand pin mapping`
- `b139dfd` (`2026-03-17`): `Create esp32_wand_controller.ino`
- `59f059e` (`2026-03-17`): `Create ir_led_test.ino`
- `2fceea9` (`2026-03-17`): `Create motor_test.ino`
- `0ac3175` (`2026-03-17`): `Create readmeforwand.md`

These commits create concrete artefacts for an ESP32-based wand path,
including:

- ESP32 firmware
- UART text protocol notes
- pin mapping documentation
- IR LED and motor test sketches
- a README describing the ESP32 motion-wand concept

### Technical character of the visible branch work

The branch work is technically coherent and focused on an ESP32/IMU-based wand
concept with:

- MPU6050-based motion sensing
- UART-based output
- IR LED triggering
- haptic motor output
- hardware setup documentation

This means the safest interpretation is **not** that the branch was empty or
purely nominal. It contains real exploratory wand-side implementation work.

### Relation to the final presented model

At the same time, the visible branch work is clearly tied to the ESP32 wand
architecture rather than the final presented LED-wand + camera + PYNQ system.

Based on the current evidence, the conservative distinction is:

- Ananya contributed concrete exploratory ESP32 wand work
- this visible branch work was **not adopted** into the final presented system
- no confirmed adopted contribution to the final LED-wand + camera + PYNQ model
  has been established from GitHub evidence alone

### Report-safe interpretation

The safest interpretation for the final report is:

`Ananya contributed a concrete exploratory ESP32 wand path, including firmware,
protocol notes, and hardware guidance. However, this work was not part of the
final adopted system because the final presented model did not use the
ESP32-based wand architecture.`

### Additional management interpretation

If needed for the project-management section, the following wording is
defensible:

`The wand-side workstream included exploratory implementation effort around an
ESP32-based wand concept. This effort should be acknowledged as real technical
work, but it should be reported separately from the final adopted system
because the project later converged on a different architecture for the
presented model.`

### Cautions

- GitHub evidence supports Ananya’s exploratory ESP32 wand work
- GitHub alone does not prove whether any non-repository support activity also
  occurred outside this branch
- the safest distinction is between `exploratory ESP32 wand contribution` and
  `adopted contribution to the final presented model`

---

## Apshara

### Planned responsibility

Apshara appears in the project record as part of the early wand-side allocation
at the planning stage.

There is also an indication in the current project chronology that Apshara may
later have become associated with backend-side work after role movement during
the project, but this should be treated carefully until the exact contribution
is confirmed.

### Current evidence status

At present, the conservative evidence base for Apshara is limited.

The accessible repository and visible GitHub branches do **not** currently show
a dedicated authored branch or authored commits that can be confidently
attributed to Apshara.

This does **not** justify concluding that no contribution existed. It only
means that the contribution is not currently evidenced strongly enough in the
accessible repository record to describe in specific technical terms.

### Safest current interpretation

The safest interpretation for report preparation is:

- Apshara had a planned role in the project
- current evidence supports discussing that planned role
- actual delivered contribution to the final presented model remains **pending
  confirmation**

### Report-safe interpretation

The safest interpretation for the final report is:

`Apshara was part of the planned team allocation during the project. However,
the exact scope of delivered technical contribution has not yet been confirmed
strongly enough to state in detail, so any final attribution should remain
limited to verified evidence.`

### Cautions

- do not convert lack of visible GitHub evidence into a stronger negative claim
- if later evidence becomes available, this note should be updated
- until then, Apshara should remain in the `pending confirmation` category

---

## Seth

### Planned responsibility

Seth appears in the project planning record as part of the backend-side team.

This places his planned role within the website / database / backend workstream
at the planning stage.

### Current evidence status

At present, the conservative evidence base for Seth is also limited.

The accessible repository and visible GitHub branches do **not** currently show
a dedicated Seth-authored branch or authored commits that can be confidently
used as direct evidence of delivered implementation work.

Again, this should be interpreted as an **evidence gap**, not as a stronger
claim than the evidence supports.

### Safest current interpretation

The safest interpretation for report preparation is:

- Seth had a planned backend role
- current accessible repository evidence does not yet confirm a delivered
  technical contribution to the final presented model
- any stronger attribution should wait until additional evidence is confirmed

### Report-safe interpretation

The safest interpretation for the final report is:

`Seth was part of the planned backend allocation for the project. However, the
current evidence base does not yet confirm a specific delivered technical
contribution strongly enough to describe in detail, so final attribution should
be limited to verified evidence only.`

### Cautions

- do not equate missing GitHub history with proof of no contribution
- if external evidence later confirms work, this note should be revised
- until then, Seth should remain in the `pending confirmation` category
