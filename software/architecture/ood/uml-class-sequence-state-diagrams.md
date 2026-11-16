---
id: software/architecture/ood/uml-class-sequence-state-diagrams
canonical_question: When should you use UML class, sequence and state diagrams, and what does each show?
aliases:
- UML sequence diagram
- UML state diagram
- UML class diagram
- lifeline activation
- state transition guard
- sơ đồ tuần tự
- sơ đồ trạng thái
- sơ đồ lớp
- model checking
entity_type: reference
domain: software > architecture > uml
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# UML Class, Sequence and State Diagrams

## TL;DR
Class diagrams show **structure**, sequence diagrams show **who talks to whom in what order** for one scenario, state diagrams show **how one object behaves over its lifetime**. Pick the diagram by the question you need answered.

| Diagram | Answers | Use for | Don't use for |
|---|---|---|---|
| Class | What exists and how it is related | Domain model, data model discussion | Showing order of events |
| Sequence | In this scenario, which participant calls which, in what order | Use-case walk-through, integration flow, finding missing responsibilities | Whole-system overview |
| State | What states can this thing be in, and what moves it between them | Approval flows, order/contract life cycles, devices | Interaction between many objects |

## Class diagram essentials
- Box with three parts: name, attributes (`name: Type`), operations (`name(params): ReturnType`).
- Visibility: `+` public, `-` private, `#` protected.
- Relations: association (line), aggregation (hollow diamond), composition (filled diamond), inheritance (hollow triangle), interface realisation (dashed line, hollow triangle).
- Multiplicity at line ends: `1`, `0..1`, `*`, `1..*`.

## Sequence diagram essentials
- Participants across the top, each with a vertical dashed **lifeline**; time runs downward.
- Solid arrow = message/call; dashed arrow = return.
- A thin rectangle on a lifeline = the participant is active.
- Frames: `alt` for alternatives (if/else), `loop` for repetition, `opt` for optional steps.
- One diagram per scenario. If it does not fit on a page, the scenario is too big or the level is too detailed.

## State diagram essentials
- Rounded box per state: name, optional state variables, activities (`entry`, `do`, `exit`).
- Arrow per transition, labelled `event [guard] / action`.
- Filled circle = initial state; circled dot = final state.
- Useful checks: is there a state with no way out? an event with no transition in some state? two transitions for the same event without distinguishing guards?

## Model checking
For systems where wrong state combinations are costly, the state model can be explored systematically: enumerate the reachable states and verify properties (no deadlock, a desired state is always reachable). Even done informally, walking every state × event cell finds missing rules before code does.

## Practical guidance
- BA: state diagrams are the fastest way to expose missing business rules in an approval or status flow.
- SA: sequence diagrams for each integration scenario, including the failure path.
- Keep diagrams as text (Mermaid/PlantUML) so they version with the code.

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
