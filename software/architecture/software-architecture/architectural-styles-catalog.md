---
id: software/architecture/software-architecture/architectural-styles-catalog
canonical_question: What are the main software architectural styles and when is each appropriate?
aliases:
- architectural styles
- layered architecture
- n-tier client server
- pipes and filters
- event-based architecture
- repository architecture
- interpreter
- process control feedback loop
- các kiểu kiến trúc phần mềm
- kiến trúc phân lớp
- chọn kiểu kiến trúc
entity_type: book_chapter
domain: software > architecture > software-architecture
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.
---

# Catalog of Architectural Styles

## TL;DR
An architectural style is a recurring way of organising components and their interactions. Each one buys some qualities and costs others. Real systems combine several; choose per subsystem from the quality requirements, not by fashion.

## Catalog
| Family | Style | Core idea | Strong on | Weak on | Typical use |
|---|---|---|---|---|---|
| Language-based | Abstract data types / object-oriented | System is a set of objects that encapsulate data and call each other | Modularity, reuse, mapping to the domain | Many small interactions; overhead for computation-heavy work | Business applications |
| Language-based | Main program and subroutine | A main routine calls a hierarchy of procedures; data passed as parameters | Simplicity, efficiency | Hard to evolve; shared data | Computation-focused programs, scripts |
| Repository | Database / shared data store | Independent components read and write a central data store | Data integrity, shared state, adding new components | Store is a bottleneck and single point of failure; schema changes ripple | Information systems, data platforms |
| Layered | Layers | Each layer serves the one above and uses the one below | Separation of concerns, replaceable layers, differing privilege levels (sandboxing) | Extra hops cost performance; temptation to skip layers | Operating systems, enterprise applications |
| Layered | Client–server, n-tier | Tiers (presentation, application logic, data) on separate machines, request–response | Scalability, centralised data and control | More infrastructure; server availability is critical | Web and mobile back ends |
| Interpreter | Interpreter | A core engine executes scripts/rules/macros written by users | Flexibility, end-user extension, portability | Slower execution; security of executed code | Rule engines, formula engines, scripting inside products |
| Dataflow | Pipes and filters | Independent filters transform data and pass it through pipes | Loose coupling, reuse and reordering of filters, parallelism | Overhead of common data format; awkward for interactive work | ETL, compilers, stream processing |
| Implicit invocation | Event-based (publish/subscribe) | Emitters publish events to a bus; consumers register interest | Very loose coupling, easy to add consumers | Order and delivery not guaranteed by default; harder to debug; shared-state races | UI frameworks, integration between systems, notifications |
| Process control | Feedback loop | Sensor → controller → actuator → process, repeating toward a set point | Self-correction | Needs measurable state and stable tuning | Device control, autoscaling, self-healing systems |

## Notes worth remembering
- **Layers vs tiers:** layers are logical separation; tiers are physical separation onto different machines.
- **Thin vs thick client:** where application logic sits in a 2-tier design. Three tiers move it to a middle tier so clients and database can change independently.
- **Event-based with shared data** needs a concurrency mechanism (e.g. semaphores/locks) or it produces race conditions.
- **Pipes and filters** work best when every filter accepts and emits the same format; otherwise conversion cost dominates.
- **Feedback loops** appear in software operations as monitor → analyse → plan → execute (autoscaling, self-healing).

## How to choose
1. List the top quality requirements (e.g. "add a new consumer without changing the producer", "process 1M rows nightly").
2. Shortlist styles strong on those qualities.
3. For each, name what it costs and whether the cost is acceptable here.
4. Apply per subsystem. A payroll platform can be n-tier overall, interpreter-based for formulas, pipes-and-filters for imports, event-based for notifications.

---
*Source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.*
