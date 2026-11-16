---
id: software/architecture/software-architecture/atam-architecture-tradeoff-analysis-method
canonical_question: How do you evaluate a software architecture with ATAM (Architecture Trade-off Analysis Method)?
aliases:
- ATAM
- Architecture Tradeoff Analysis Method
- utility tree
- architecturally significant requirements
- ASR
- sensitivity point
- trade-off point
- risk themes
- đánh giá kiến trúc
- phương pháp ATAM
- cây tiện ích
entity_type: how_to
domain: software > architecture > software-architecture
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.
---

# Evaluating an Architecture with ATAM

## TL;DR
ATAM (from the Software Engineering Institute, Carnegie Mellon) evaluates an architecture against prioritised quality scenarios. Its outputs are **risks, non-risks, sensitivity points and trade-offs**, grouped into risk themes tied to business drivers. Evaluators do not need prior knowledge of the system.

## Participants
| Group | Who | Role |
|---|---|---|
| Evaluation team | Designers; peers (on the project, not in the design); outsiders (external experts) | Run the method, must stay unbiased |
| Project decision makers | Project manager, client, product owner, architect, technical lead | Present business drivers and architecture; have authority to change it |
| Architecture stakeholders | End users, developers, support staff, anyone affected | Supply and prioritise scenarios |

## The nine steps
| # | Step | Result |
|---|---|---|
| 1 | Present ATAM | Shared expectations about process and outputs |
| 2 | Present business drivers | Business problem, goals, constraints, scope |
| 3 | Present the architecture | Current and target state, constraints of time, cost, quality |
| 4 | Identify architectural approaches | Patterns and styles actually used |
| 5 | Create the quality attribute utility tree | Utility → quality attributes → refinements → ASRs, each rated (H/M/L) for importance and difficulty |
| 6 | Analyse architectural approaches | For high-priority ASRs: risks, non-risks, sensitivity points, trade-offs |
| 7 | Brainstorm and prioritise scenarios | Stakeholders' own scenarios, merged and voted |
| 8 | Re-analyse approaches | Repeat the analysis for the top 5–10 stakeholder scenarios |
| 9 | Present results | Documents, utility tree, findings grouped by risk theme |

If the stakeholder scenarios in step 7 differ widely from the utility tree of step 5, that is itself a finding: the architecture was aimed at the wrong priorities.

## Vocabulary
| Term | Meaning |
|---|---|
| ASR | Architecturally significant requirement: a quality requirement that shapes the architecture |
| Risk | A decision that may lead to a quality requirement not being met |
| Non-risk | A decision judged safe for the scenario |
| Sensitivity point | A component or parameter to which a quality measure is highly sensitive |
| Trade-off point | A decision that affects more than one quality in opposite directions |
| Risk theme | A group of related risks, linked to the business driver they threaten |

## Lightweight version for small teams
1. Write 5–10 concrete quality attribute scenarios with the product owner.
2. Rate each H/M/L on importance and difficulty; keep the (H, H) and (H, M) ones.
3. For each, walk the architecture and label it risk, non-risk, sensitivity or trade-off, with one sentence of reasoning.
4. Group risks into themes and decide: fix now, accept, or monitor.

## Worked illustration
A sharing app stores everything in local files on one device. Scenario "search under heavy load returns in under 1 second" → **risk** (whole data set loaded and filtered in memory). Scenario "account stored in an external shared database" → **trade-off** (interoperability vs latency and a new single point of failure). Scenario "login response time" → **sensitivity point** (depends on external read latency; a local session cache changes it). Risk theme: no remote data layer or concurrency control, threatening the multi-user business goal.

---
*Source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.*
