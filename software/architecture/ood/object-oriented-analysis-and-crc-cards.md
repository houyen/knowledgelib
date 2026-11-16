---
id: software/architecture/ood/object-oriented-analysis-and-crc-cards
canonical_question: How do you go from requirements to a first object-oriented design using CRC cards?
aliases:
- CRC cards
- Class Responsibility Collaborator
- object-oriented analysis and design
- conceptual design vs technical design
- thẻ CRC
- phân tích hướng đối tượng
- từ yêu cầu ra thiết kế
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# From Requirements to Objects: OO Analysis and CRC Cards

## TL;DR
Design sits between requirements and code. Do it in two passes — **conceptual design** (what components exist, what each is responsible for, how they connect) and **technical design** (how each responsibility is fulfilled). CRC cards are a cheap, throw-away way to do the conceptual pass with the people who know the domain.

## The two design passes
| Pass | Question | Typical artefact | Who reviews |
|---|---|---|---|
| Conceptual | Which components, which responsibilities, which connections? | Mock-ups, CRC cards | Client, users, BA |
| Technical | How is each responsibility implemented? | UML class diagrams, technical diagrams | Developers, architect |

If the technical pass turns out not to be feasible, go back and change the conceptual design, and tell the client what the compromise is. Hiding the compromise is the usual way a project drifts from what was asked.

## CRC card
One index card per candidate component:

| Section | Content |
|---|---|
| **C**lass (top) | Name of the component |
| **R**esponsibilities (left) | What it knows and what it does |
| **C**ollaborators (right) | Other components it needs to fulfil those responsibilities |

## How to run a CRC session
1. Start from user stories or scenarios; nouns are candidate components, verbs are candidate responsibilities.
2. Write one card per component. Keep responsibilities short; a card that overflows is a component that should be split.
3. Lay cards on a table, place collaborators next to each other.
4. **Simulate** a scenario by walking through the cards: who receives the request, who is asked next. Missing responsibilities and missing components show up as gaps in the walk.
5. Rewrite or discard cards freely. The point of paper is that it is cheap to be wrong.

## Design for quality, not only function
- Requirements include **quality attributes** (performance, security, maintainability…), and these often conflict; e.g. extra security checks cost performance.
- Every design choice has **context** and **consequences**: the same solution is right in one setting and wrong in another.
- Make trade-offs explicit and get them agreed, instead of silently optimising one quality.

## When to use
- Early discovery with non-technical stakeholders.
- Before committing to class diagrams or a data model.
- As a quick check of a proposed design: can the cards carry every scenario?

## Limits
CRC cards do not show timing, data volumes or deployment. Move to sequence diagrams and architecture views once the conceptual shape is stable.

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
