---
id: software/architecture/ood/liskov-substitution-and-inheritance-pitfalls
canonical_question: When is inheritance appropriate, and what does the Liskov Substitution Principle require?
aliases:
- Liskov Substitution Principle
- LSP
- inheritance pitfalls
- generalization principles
- subtype substitution
- nguyên lý thay thế Liskov
- khi nào dùng kế thừa
- inheritance vs composition
entity_type: book_chapter
domain: software > architecture > object-oriented-design
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.
---

# Liskov Substitution and Inheritance Pitfalls

## TL;DR
Use inheritance only when a subclass can stand in for its base class **everywhere** without the caller noticing. If the subclass has to disable, weaken or change the meaning of inherited behaviour, the relation is not a true subtype: use decomposition (composition/delegation) instead.

## Two tests before inheriting
1. **Does the subclass add something of its own?** If it only renames the base class, the hierarchy adds nothing.
2. **Substitution test:** can an instance of the subclass be used wherever the base class is expected, with the program still behaving correctly?

## What substitution requires
A subclass may add or specialise behaviour, but it must respect the base class contract:
- It must not change what a base method **means** (a method that returns a value must not start returning something of different meaning).
- It must not demand **more** from callers than the base did (no stricter preconditions).
- It must not promise **less** than the base did (no weaker postconditions).
- Invariants of the base class still hold.
- It must not make inherited behaviour unusable (throwing "not supported" is the classic violation).

## Typical violations
| Smell | Why it breaks |
|---|---|
| Subclass overrides a method to do nothing or throw | Caller written against the base now fails |
| Subclass uses the base only to reuse some code (stack extends list) | Inherits operations that break its own rules |
| Callers check the concrete type before calling | The hierarchy is not substitutable; polymorphism is fake |

## What to do instead
- Reuse without "is-a": hold the other class as a field and delegate to it.
- Shared contract without shared implementation: use an interface.
- Variants of behaviour: move the varying part into a separate object.

## Why it matters outside code
The same rule applies to APIs and data contracts: a new version of a service or a schema should be usable by existing consumers without change. A v2 that requires more input or returns less is a breaking change, whatever the version number says.

Source note: also summarises the short reading *Liskov's Substitution Principle* from the same course.

---
*Source: Summary in our own words of *Object-Oriented Design — Course Notes* (University of Alberta, Software Design and Architecture specialization, 2017). Not a verbatim copy.*
