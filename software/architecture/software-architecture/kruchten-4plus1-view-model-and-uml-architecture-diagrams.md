---
id: software/architecture/software-architecture/kruchten-4plus1-view-model-and-uml-architecture-diagrams
canonical_question: What is Kruchten's 4+1 view model and which UML diagram documents each architectural view?
aliases:
- 4+1 view model
- Kruchten
- logical process development physical view
- component diagram
- package diagram
- deployment diagram
- activity diagram
- mô hình 4+1
- góc nhìn kiến trúc
- sơ đồ thành phần triển khai
entity_type: book_chapter
domain: software > architecture > software-architecture
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.
---

# Kruchten's 4+1 View Model and UML Architecture Diagrams

## TL;DR
No single diagram describes an architecture, because stakeholders ask different questions. The 4+1 model gives four views — **logical, process, development, physical** — tied together by **scenarios** (the "+1"). Pick the UML diagram that matches the view.

## The views
| View | Concern | Main audience | Typical UML |
|---|---|---|---|
| Logical | Functionality: key objects and their relations | End users, analysts | Class diagram, state diagram |
| Process | Run-time behaviour: processes, concurrency, performance, order of activities | Integrators, performance engineers | Activity diagram, sequence diagram |
| Development | How the code is organised: modules, packages, libraries, team ownership | Developers, project managers | Component diagram, package diagram |
| Physical | Where software runs: nodes, networks, mapping of software to hardware | Operations, infrastructure | Deployment diagram |
| +1 Scenarios | Use cases that exercise all four views and check they agree | Everyone | Use cases, user stories |

Not every system needs all four. A small single-process application may skip the process and physical views; say so explicitly instead of leaving them blank.

## Diagram cheat sheet
| Diagram | Shows | Key notation | Use it to |
|---|---|---|---|
| Component | Components and the interfaces between them | Provided interface = ball (lollipop); required interface = socket; ball-in-socket = assembly | Find what can be replaced or developed independently; show dependency direction |
| Package | Grouping of related elements and dependencies between groups | Tabbed folder; dashed arrow = dependency; `import` / `merge` | Plan namespaces, modules, release units; spot cyclic dependencies |
| Deployment | Nodes (devices, execution environments) and the artefacts deployed on them | 3-D box = node; artefact inside; lines = communication paths | Capacity, network and environment discussions; go-live planning |
| Activity | Flow of control from one activity to the next | Rounded box = activity; diamond = decision; bar = fork/join; swimlanes = responsibility | Business process and workflow modelling, parallel work |

## How to produce an architecture description
1. Collect scenarios that matter (highest-value use cases plus the hardest quality requirements).
2. Draw the logical view for the core domain.
3. Add the development view: which components, which team owns each.
4. Add process and physical views only where concurrency, scale or deployment constraints exist.
5. Walk each scenario through every view; anything a scenario needs that a view cannot show is a gap.

## Common mistakes
- One "architecture diagram" mixing classes, servers and data flows.
- Views that contradict each other because no scenario was traced through them.
- Deployment diagram drawn once and never updated after infrastructure changes.

Related: the C4 model (context, container, component, code) is a later, lighter alternative with similar intent.

---
*Source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.*
