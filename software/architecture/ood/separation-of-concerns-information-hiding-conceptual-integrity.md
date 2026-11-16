---
id: software/architecture/ood/separation-of-concerns-information-hiding-conceptual-integrity
canonical_question: What do separation of concerns, information hiding and conceptual integrity mean in software design?
aliases:
- separation of concerns
- information hiding
- conceptual integrity
- design consistency
- tách biệt mối quan tâm
- che giấu thông tin
- tính nhất quán khái niệm
- access modifiers
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# Separation of Concerns, Information Hiding, Conceptual Integrity

## TL;DR
Three principles that keep a design changeable: put each concern in its own place, expose only what others need, and make the whole system look as if one mind designed it.

## Separation of concerns
A **concern** is anything that matters to solving the problem: a piece of data, a behaviour, a policy. Each concern gets its own module so it can be changed without touching the others.

How to find concerns that should be separated:
- Things that change for different reasons (business rule vs screen layout vs storage).
- Things that different people own.
- Behaviour that only some variants have (move it out of the general class).

It is the principle underneath the other four: abstraction picks the concerns, encapsulation groups each one, decomposition splits them, generalization shares the common ones.

## Information hiding
A module shows other modules only what they need to use it. The rest — representation, algorithm, internal state — stays hidden, so it can change freely.

| Access level (Java) | Visible to |
|---|---|
| public | Everyone |
| protected | Same package and subclasses |
| default (no modifier) | Same package |
| private | The class only |

Guidelines:
- Start private; widen only when a real caller needs it.
- Expose behaviour, not data. A getter that returns an internal collection leaks the representation.
- At system level the same idea applies to APIs: publish a contract, never a table.

## Conceptual integrity
The system follows consistent decisions, so knowing one part helps you understand the rest. It is not "everyone agrees"; it is that decisions, once made, are applied everywhere.

Ways to get it:
- Shared conventions and code reviews.
- A small group (or one architect) owning the core design decisions.
- A well-defined base design/architecture that additions must fit.
- Agile practices that keep communication frequent: stand-ups, retrospectives.

Signs it is missing: three ways to do the same thing, naming that changes per module, each team's part of the system looking like a different product.

## For reviewers
| Question | Principle |
|---|---|
| If this rule changes, how many files change? | Separation of concerns |
| What would break if this class changed its internal data structure? | Information hiding |
| Does the new feature follow the existing pattern, or introduce a second one? | Conceptual integrity |

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
