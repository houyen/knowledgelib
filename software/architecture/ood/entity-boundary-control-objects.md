---
id: software/architecture/ood/entity-boundary-control-objects
canonical_question: What are entity, boundary and control objects in object-oriented design?
aliases:
- entity boundary control
- ECB pattern
- categories of objects
- boundary object
- control object
- đối tượng thực thể biên điều khiển
- phân loại đối tượng trong thiết kế
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of the short reading *Categories of Objects in Design* (University of Alberta, Object-Oriented Design course). Not a verbatim copy.
---

# Entity, Boundary and Control Objects

## TL;DR
When you break a problem into objects you get three kinds. **Entity** objects model things in the problem domain, **boundary** objects talk to the outside (users, other systems), **control** objects coordinate the others. Software made only of entities ends up with business objects that also draw screens and call networks.

| Category | Responsibility | Found when | Examples |
|---|---|---|---|
| Entity | Knows its own attributes and the rules for changing them | First, during analysis of the domain | Customer, Order, Contract, Payslip |
| Boundary | Sits between the system and something outside it | During technical design | Screen/view, API client, file importer, message listener |
| Control | Coordinates a flow across several objects | When an entity becomes too large or objects need a mediator | Use-case handler, workflow coordinator, mediator |

## Why separate them
- Entities stay stable while screens and integrations change.
- Boundary objects absorb changes in external formats and protocols.
- Control objects hold the sequence of a use case, so entities do not need to know about each other (looser coupling).

## How to apply
1. Derive entities from the nouns of user stories and the business glossary.
2. For every actor or external system touching the scenario, add a boundary object.
3. For every use case with more than a trivial sequence, add a control object.
4. Check: an entity should not import UI or network code; a boundary should not contain business rules.

## Relation to other structures
The split is the seed of MVC (model = entity, view = boundary, controller = control) and of layered and hexagonal architectures (domain, adapters, application services).

---
*Source: Summary in our own words of the short reading *Categories of Objects in Design* (University of Alberta, Object-Oriented Design course). Not a verbatim copy.*
