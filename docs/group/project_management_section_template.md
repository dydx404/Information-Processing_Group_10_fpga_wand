# Project Management Section Template

This document is a **report-writing template** for the project management
section of a formal group engineering report.

It is designed for a case where:

- the project was formally structured as a group effort
- responsibilities were assigned at the outset
- actual delivery may not have matched the original allocation
- critical-path work may have become concentrated
- project management, coordination, and recovery actions are important to explain

This template is intentionally neutral and evidence-focused. It should be
populated later with verifiable facts, not assumptions.

---

## How To Use This Template

- Replace bracketed prompts with factual content
- Keep statements linked to evidence where possible
- Distinguish clearly between **planned responsibility** and **actual delivery**
- Describe changes in ownership professionally, without assigning blame
- Emphasise impact on delivery, coordination, risk, and management response
- Use the **final presented model** as the reference point when discussing
  actual delivery
- Record exploratory or non-adopted work separately rather than treating it as
  equivalent to final adopted implementation
- If a contribution is still being confirmed, mark it as **unverified** rather
  than inferring ownership
- If the final delivery phase involved rapid shared debugging and testing,
  record that collaboration explicitly rather than forcing all contribution into
  a single-owner narrative

Recommended supporting evidence:

- original role allocation or planning notes
- milestone plan or roadmap
- task tracker or action lists
- meeting notes or coordination records
- implementation ownership evidence
- commit history or document history
- test/integration outcomes
- final deliverable status

### Evidence Standard For Attribution

Use the following conservative rule when later filling the section:

- **Planned responsibility**: what a person or subgroup was originally expected
  to do
- **Confirmed adopted contribution**: work that can be evidenced and that was
  used in the final presented system
- **Exploratory or partial contribution**: work that existed, informed
  discussion, or reached partial implementation, but was not part of the final
  adopted model
- **Unverified contribution**: work that may have occurred but is not yet
  confirmed strongly enough to state as fact

This separation helps the final report remain professional and defensible.

---

## Recommended Section Title

`Project Management, Task Allocation, and Delivery Review`

Alternative formal titles:

- `Project Management and Team Delivery`
- `Team Organisation, Delivery, and Project Control`
- `Project Coordination, Ownership, and Delivery Outcomes`

---

## Suggested Overall Flow

Use the section in this order:

1. Explain the intended management structure
2. Set out the planned team responsibilities
3. Record the actual task allocation and completion outcomes
4. Compare planned responsibility against actual delivery
5. Identify ownership of critical-path work
6. Explain coordination, dependency management, and escalation
7. Evaluate risks, recovery actions, and delivery control
8. Reflect on workload balance, accountability, and lessons learned

This sequence helps the writing remain analytical and professional.

---

## 1. Project Management Approach

### 1.1 Purpose of this section

**What this subsection should do**

- define the scope of the project management discussion
- explain that the section assesses how work was planned, allocated,
  coordinated, and delivered
- signal that the analysis is based on evidence rather than personal opinion

**Prompt**

`This section evaluates how the project was organised, how responsibilities were initially assigned, how work was actually delivered, and how management decisions affected final outcomes. The discussion distinguishes between planned ownership and actual implementation in order to provide a fair and evidence-based account of team delivery.`

### 1.2 Basis of analysis and evidence sources

**What this subsection should do**

- identify the sources that will support the later analysis
- reassure the reader that claims about ownership and progress are grounded

**Prompt**

`The analysis in this section is based on [planning artefacts], [task records], [implementation history], [meeting records], and [final deliverables]. These sources are used to compare intended task allocation with actual delivery and to assess how project management affected progress.`

---

## 2. Planned Team Structure and Intended Responsibilities

### 2.1 Original role allocation

**What this subsection should do**

- state how the group intended to divide work at the start
- describe responsibilities by role or workstream
- keep this factual and neutral

**Template table**

| Team member / role | Intended responsibility area | Expected outputs | Planned dependencies |
| --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |

### 2.2 Planned work packages and deliverables

**What this subsection should do**

- define the main work packages
- show the project as a set of deliverables rather than only individual people
- support later comparison against actual delivery

**Template table**

| Work package | Intended owner | Planned deliverable | Planned milestone / timing | Downstream dependency |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |

### 2.3 Initial dependencies and critical-path assumptions

**What this subsection should do**

- explain which tasks were expected to gate integration or final delivery
- identify where delays in one area would affect others

**Prompt**

`At the planning stage, the project depended on several linked workstreams. In particular, [insert task areas] formed the anticipated critical path because progress in [insert dependent areas] required those components to be completed first.`

---

## 3. Actual Task Allocation and Delivery

### 3.1 Actual distribution of work

**What this subsection should do**

- describe what happened in practice
- record which tasks were actually delivered by which person
- avoid judgemental language; focus on execution

**Template table**

| Work package | Intended owner | Actual primary contributor | Actual support contributors | Final delivery status |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] | [Completed / partial / reassigned / not delivered] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Completed / partial / reassigned / not delivered] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Completed / partial / reassigned / not delivered] |

### 3.2 Progress and completion status by task

**What this subsection should do**

- summarise the outcome of each major task
- show which work reached usable completion and which did not

**Template table**

| Task / deliverable | Status | Evidence of completion | If incomplete, what remained outstanding |
| --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |

### 3.2A Adopted versus non-adopted outputs

**What this subsection should do**

- separate work that directly contributed to the final presented model from work
  that remained exploratory, partial, or non-adopted
- allow fair acknowledgement without overstating final implementation ownership

**Template table**

| Artefact / work item | Contributor(s) | Status relative to final model | Evidence basis | Suggested report treatment |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Adopted / partial / exploratory / not adopted / unverified] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Adopted / partial / exploratory / not adopted / unverified] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Adopted / partial / exploratory / not adopted / unverified] | [Insert] | [Insert] |

### 3.3 Changes in ownership over time

**What this subsection should do**

- document where tasks moved from one owner to another
- explain why, using factual project-management reasoning

**Prompt structure**

`During implementation, ownership changed in several areas. [Task] was originally assigned to [planned owner] but was later delivered by [actual owner / owners]. This change occurred because [insert evidence-based reason, e.g. missed milestone, integration urgency, technical blocker, scope shift]. The effect of this reallocation was [insert delivery consequence].`

---

## 4. Variance Between Planned Responsibility and Actual Delivery

### 4.1 Areas of alignment

**What this subsection should do**

- show fairness by identifying where planned and actual ownership matched
- avoid making the section read as purely critical

**Prompt**

`Several parts of the project remained aligned with the original plan. In particular, [insert work areas] were delivered broadly in line with their intended ownership, which reduced coordination overhead and supported predictable progress.`

### 4.2 Areas of divergence

**What this subsection should do**

- identify where actual delivery departed from planned allocation
- present this as a management issue, not a personal grievance

**Template table**

| Work area | Planned owner | Actual owner | Nature of variance | Delivery impact |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Reassigned / partially delivered / absorbed by another member] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Reassigned / partially delivered / absorbed by another member] | [Insert] |

### 4.3 Management implications of the variance

**What this subsection should do**

- analyse the consequences of mismatched ownership
- focus on schedule, integration, workload concentration, and risk

**Prompt**

`The main consequence of these divergences was that delivery became more concentrated around [insert workstream or role], increasing integration dependency and creating schedule risk. This also altered the coordination burden, because [insert reasoned effect].`

---

## 5. Critical-Path Ownership and Delivery Control

### 5.1 Identification of critical-path work

**What this subsection should do**

- identify the tasks that determined whether the project could be completed
- tie this to integration and final assessment readiness

**Prompt**

`Although multiple workstreams contributed to the final system, a smaller set of tasks formed the effective critical path. These included [insert tasks], because the project could not reach an integrated and demonstrable state without them.`

### 5.2 Ownership of critical-path implementation

**What this subsection should do**

- show who actually carried the decisive implementation work
- highlight leadership and implementation ownership in a factual way

**Template table**

| Critical-path task | Why it was critical | Planned owner | Actual owner | Outcome |
| --- | --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] | [Insert] |

### 5.3 Effect on overall project outcome

**What this subsection should do**

- explain how critical-path ownership affected the project result
- show whether intervention, leadership, or reallocation protected delivery

**Prompt**

`Control of critical-path work had a direct effect on project completion. In practice, progress depended on [insert ownership pattern], which meant that delivery of the final integrated system relied on [insert evidence-based explanation of who ensured completion and how].`

### 5.4 Final integration phase and shared delivery effort

**What this subsection should do**

- create space for a fair account of late-stage joint work
- distinguish between primary implementation ownership and collaborative final
  testing / debugging / recovery
- allow recognition of committed contributors without overstating authorship of
  the full final system

**Prompt**

`Although implementation ownership of major subsystems may have been concentrated, the final pre-demonstration phase involved shared rapid development, testing, and debugging activity. This should be described separately so that collaborative final delivery effort can be recognised accurately without obscuring primary ownership of the underlying implementation.`

---

## 6. Coordination, Communication, and Dependency Management

### 6.1 Coordination mechanisms

**What this subsection should do**

- explain how the group attempted to manage work
- describe meetings, check-ins, progress reviews, demonstrations, or task tracking

**Prompt**

`Coordination was managed through [insert mechanisms], which were intended to provide visibility over progress, clarify ownership, and support integration across workstreams.`

### 6.2 Dependency management

**What this subsection should do**

- explain how interdependent tasks were handled
- describe whether dependencies were explicit, monitored, and reviewed

**Prompt**

`The project contained several technical and organisational dependencies. These were managed by [insert process], with particular attention to [insert interfaces, integration points, or milestone dependencies].`

### 6.3 Escalation and decision-making

**What this subsection should do**

- explain how unresolved issues or missed commitments were handled
- present escalation as a project-control mechanism

**Prompt**

`Where progress fell behind or ownership became unclear, escalation took the form of [insert approach]. Decisions on reassignment, scope reduction, or recovery priority were made through [insert process], with the goal of preserving end-to-end delivery.`

---

## 7. Risk Management, Issue Response, and Recovery

### 7.1 Key project risks

**What this subsection should do**

- identify the main delivery risks relevant to management
- include coordination and dependency risks, not just technical ones

**Template table**

| Risk | Why it mattered | Likely impact | Planned mitigation |
| --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |

### 7.2 Issues that materialised

**What this subsection should do**

- record which risks actually happened
- describe them factually and in relation to delivery

**Template table**

| Issue encountered | Related risk | Effect on schedule / scope / integration | Immediate consequence |
| --- | --- | --- | --- |
| [Insert] | [Insert] | [Insert] | [Insert] |
| [Insert] | [Insert] | [Insert] | [Insert] |

### 7.3 Recovery and mitigation actions

**What this subsection should do**

- explain what the group did in response
- allow you to show intervention, reallocation, and management action clearly

**Prompt**

`When these issues materialised, recovery actions included [insert actions such as reassignment, schedule compression, direct implementation, scope control, or additional integration work]. These responses were taken to reduce the risk of non-delivery and to preserve the final demonstrable system.`

---

## 8. Evaluation of Workload Balance and Accountability

### 8.1 Workload balance

**What this subsection should do**

- assess whether work remained proportionately distributed
- focus on actual delivery effort, not nominal assignment

**Prompt**

`Although the project began with a nominally distributed allocation of responsibilities, the actual workload over time became [insert balanced / uneven / progressively concentrated], particularly in relation to [insert task areas].`

### 8.2 Accountability and follow-through

**What this subsection should do**

- evaluate whether assigned work was delivered by the intended owner
- frame the discussion around reliability, visibility, and follow-through

**Prompt**

`From a project-management perspective, accountability depended not only on assigned ownership but on whether tasks were carried through to a usable state. In several areas, this was achieved as planned; in others, delivery required reassignment or intervention to maintain progress.`

### 8.3 Leadership and management contribution

**What this subsection should do**

- create explicit space to highlight coordination leadership
- recognise implementation ownership, integration control, and recovery effort
- do this without sounding personal or accusatory

**Prompt**

`A significant management contribution can be identified in [insert planning, coordination, implementation, integration, or recovery area]. This contribution was important because it provided [insert visibility, delivery control, dependency management, or direct completion of critical work].`

---

## 9. Reflection and Project Management Lessons

### 9.1 Management strengths

**What this subsection should do**

- identify what worked in the group’s management approach
- keep this grounded in outcomes

**Prompt**

`The strongest aspects of project management were [insert strengths], particularly because they supported [insert effect on delivery, integration, or recovery].`

### 9.2 Management weaknesses

**What this subsection should do**

- discuss structural weaknesses in planning, tracking, accountability, or escalation
- keep the language analytical

**Prompt**

`The main weaknesses in project management were not primarily technical, but organisational. In particular, [insert weaknesses] reduced predictability and increased the burden on recovery and integration.`

### 9.3 Lessons for future group engineering projects

**What this subsection should do**

- conclude with general lessons rather than personal criticism
- show maturity and professionalism

**Prompt**

`A key lesson from this project is that nominal task allocation is not sufficient on its own. Effective delivery requires early visibility of slippage, explicit ownership of critical-path work, timely reassignment when necessary, and coordination structures that convert planned roles into actual completed outputs.`

---

## Optional Closing Paragraph Template

`Overall, the project management record shows a distinction between the original distribution of responsibilities and the pattern of actual delivery that emerged during implementation. The final outcome depended not only on technical execution, but also on how ownership, coordination, risk response, and delivery control were managed as the project evolved.`

---

## Writing Guidance: Professional Tone

Prefer language such as:

- `planned allocation`
- `actual delivery`
- `ownership shifted`
- `work was reallocated`
- `delivery became concentrated`
- `this created dependency risk`
- `recovery action was required`
- `critical-path work`
- `implementation ownership`
- `coordination burden`

Avoid language such as:

- `someone did nothing`
- `unfair`
- `I had to do everything`
- `others failed`
- `blame`

A strong academic tone focuses on:

- evidence
- delivery outcomes
- management implications
- recovery actions
- lessons learned

---

## Optional Evidence Matrix

Use this if you want to keep a private mapping between claims and evidence
before writing the final report.

| Claim to support | Evidence source | Where it will appear in the report |
| --- | --- | --- |
| [Insert] | [Insert] | [Section / subsection] |
| [Insert] | [Insert] | [Section / subsection] |
| [Insert] | [Insert] | [Section / subsection] |
