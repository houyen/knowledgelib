---
id: software/architecture/ood/four-design-principles-abstraction-encapsulation-decomposition-generalization
canonical_question: What are the four core object-oriented design principles and how do they show up in UML class diagrams?
aliases:
- abstraction encapsulation decomposition generalization
- four OO design principles
- association aggregation composition
- inheritance vs interface
- bốn nguyên lý hướng đối tượng
- trừu tượng đóng gói phân rã tổng quát hoá
- UML class diagram
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# The Four OO Design Principles

## TL;DR
Abstraction decides **what matters**, encapsulation decides **what is hidden**, decomposition decides **how the whole is split**, generalization decides **what is shared**. Each has a direct notation in a UML class diagram.

## Summary table
| Principle | Idea | Rule of thumb | UML / code form |
|---|---|---|---|
| Abstraction | Keep only attributes and behaviours relevant to the context | The same real thing has different abstractions in different systems; re-check when context changes | Class box: name, attributes, operations |
| Encapsulation | Bundle data with the operations on it; expose an interface, restrict the rest | Callers depend on *what* a class does, not *how* | Visibility: `+` public, `-` private, `#` protected; getters/setters |
| Decomposition | Split a whole into parts with clear responsibilities | Parts can be fixed or dynamic in number, and can be shared or exclusive | Association, aggregation, composition |
| Generalization | Factor common attributes/behaviour into one place | Don't repeat yourself; but only generalize real "is-a" relations | Inheritance (solid line, hollow arrow), interfaces (dashed) |

## Three kinds of decomposition
| Relation | Meaning | Lifetime | UML |
|---|---|---|---|
| Association | Loose, "uses / knows about" | Independent | Plain line |
| Aggregation | Weak "has-a"; part can exist without the whole | Independent | Hollow diamond at the whole |
| Composition | Strong "has-a"; part has no meaning without the whole | Part dies with the whole | Filled diamond at the whole |

Choosing between aggregation and composition is a statement about ownership and deletion. It matters for data models as much as for classes (cascade delete or not).

## Generalization: inheritance vs interface
| | Inheritance | Interface |
|---|---|---|
| Shares | Attributes and implemented behaviour | Only the contract (signatures) |
| Relation | Subclass is a subtype of the superclass | Class promises to provide behaviours |
| Risk | Tight coupling to the base class | None on implementation; more boilerplate |
| Use when | Subtype truly behaves like the base in every context | Unrelated classes must be used the same way |

## Why the principles matter to non-developers
- A **BA** applies abstraction when choosing which attributes of a business entity belong in scope.
- An **SA** applies decomposition and encapsulation at service level: what a service owns, what it exposes.
- A **data** designer applies composition/aggregation when deciding ownership and referential rules.

## Common mistakes
- Abstraction that copies the real world instead of the problem context (too many attributes).
- Public fields "for convenience" — every caller becomes coupled to the representation.
- Inheritance used for code reuse where there is no "is-a" relation; prefer decomposition.

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
