---
id: software/architecture/software-architecture/quality-attributes-and-quality-attribute-scenarios
canonical_question: How do you specify measurable quality attributes (non-functional requirements) with quality attribute scenarios?
aliases:
- quality attributes
- quality attribute scenario
- non-functional requirements
- NFR
- stimulus response measure
- availability performance security usability
- maintainability testability
- thuộc tính chất lượng
- yêu cầu phi chức năng đo được
- kịch bản thuộc tính chất lượng
entity_type: book_chapter
domain: software > architecture > software-architecture
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.
---

# Quality Attributes and Quality Attribute Scenarios

## TL;DR
An architecture is not good or bad in itself; it is right or wrong for a set of requirements in a context. Quality attributes are the **measurable** properties used to judge it. Write each one as a scenario with six parts so it can be tested and argued about.

## Common attributes
| Perspective | Attribute | What is measured |
|---|---|---|
| Developer | Maintainability | Ease of making changes over the system's life |
| Developer | Reusability | How much of the system can be used elsewhere |
| Developer | Flexibility | How well it adapts to requirement changes |
| Developer | Modifiability | Ability to cope with changes, add features, switch technology |
| Developer | Testability | How easily correctness can be demonstrated |
| Developer | Conceptual integrity | Consistency of design decisions across the system |
| User | Availability | Share of time the system is running and able to respond (uptime) |
| User | Interoperability | Ability to exchange and understand data with other systems |
| User | Security | Protection of data from unauthorised access; integrity and authentication |
| User | Performance | Throughput and latency under a given load |
| User | Usability | Ease of learning and using the system to reach goals |

Different stakeholders weight these differently (users rarely ask for testability, developers do). Prioritise explicitly and accept compromises.

## The six-part scenario
| Part | Meaning | Example |
|---|---|---|
| Stimulus source | Who or what triggers it | End user |
| Stimulus | The condition arriving | Clicks "search" |
| Artifact | Part of the system affected | Mobile app + item service |
| Environment | State when it happens | Heavy load, 1,000 concurrent users |
| Response | What the system does | Displays the list of matching items |
| Response measure | How success is measured | Results shown within 1 second for 95% of requests |

**General scenarios** describe the attribute for any system; **concrete scenarios** fill in real values for yours. Only concrete scenarios are testable.

## Writing good scenarios
- Include failure and abnormal environments (peak load, dependency down, concurrent edits), not only the normal case.
- The response measure must be a number with a unit and a condition.
- One scenario, one stimulus. Split compound ones.
- Rank scenarios by business importance and by difficulty; the important-and-hard ones drive the architecture.

## Availability example
Stimulus: database node becomes unreachable. Environment: normal operations. Response: requests are served from a replica and operators are notified. Measure: no more than 30 seconds of failed requests; no committed data lost.

## Rules a good architecture tends to follow
Design side: well-defined components with clear responsibilities, information hiding, consistent ways of doing things, and a small team or single architect owning technical decisions. Process side: requirements prioritised, architecture documented in views, evaluated early against scenarios, and allowing incremental implementation.

---
*Source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.*
