---
id: software/architecture/ood/coupling-cohesion-design-complexity
canonical_question: How do you evaluate design complexity with coupling and cohesion?
aliases:
- coupling and cohesion
- loose coupling high cohesion
- degree ease flexibility of coupling
- design complexity
- độ kết dính và độ phụ thuộc
- đánh giá độ phức tạp thiết kế
- module coupling
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# Coupling and Cohesion: Evaluating Design Complexity

## TL;DR
A design is too complex when a person cannot keep the relevant part in their head. Two measures tell you where: **coupling** (how much a module depends on others — want it loose) and **cohesion** (how focused a module is on one purpose — want it high).

## Coupling — three questions per module
| Dimension | Question | Good | Bad |
|---|---|---|---|
| Degree | How many connections does it have to other modules? | Few | Many |
| Ease | How obvious are those connections? | Visible through the interface, no need to read internals | Requires knowing the other module's implementation |
| Flexibility | How easily can the other module be swapped? | Replaceable behind the same interface | Replacement forces changes here |

Think of a puzzle piece (fits one place only: tight) versus a Lego brick (fits anywhere: loose).

## Cohesion
A module is highly cohesive when it does one thing and everything inside serves that thing. Low cohesion signs:
- The name needs "and" or "manager/util/helper".
- Methods use disjoint subsets of the fields.
- Different stakeholders ask for changes to the same module for unrelated reasons.

Fix low cohesion by splitting along purposes. Splitting raises the number of modules, which can raise coupling, so the two measures are balanced, not maximised separately.

## Quick review checklist
1. For each module, list what it depends on. More than a handful → look for a missing abstraction.
2. Can you describe the module's purpose in one sentence without "and"?
3. Could a new team member use the module from its interface alone?
4. If a dependency were replaced (database, vendor API), how many modules change?

## Applying it above class level
The same measures work for services, pipelines and teams:
- Service coupling: shared database tables, synchronous call chains, shared deploy schedule.
- Pipeline cohesion: one job that extracts, cleans, aggregates and emails is low cohesion.
- Integration flexibility: a canonical message format lets one side change without the other.

## Trade-off
Removing every dependency is not the goal; a system with zero coupling does nothing. Aim for dependencies that are few, explicit, and pointing at stable interfaces.

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
