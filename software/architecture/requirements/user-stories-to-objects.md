---
id: software/architecture/requirements/user-stories-to-objects
canonical_question: How do you write a user story and derive design objects and further requirements from it?
aliases:
- user story format
- As a I want so that
- nouns and verbs analysis
- expressing requirements with user stories
- viết user story
- câu chuyện người dùng
- từ user story ra đối tượng
- requirements elicitation
entity_type: how_to
domain: software > architecture > requirements
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of the short reading *Expressing Requirements with User Stories* (University of Alberta, Object-Oriented Design course), extended with common practice (INVEST, acceptance criteria). Not a verbatim copy.
---

# User Stories: Format and Deriving Objects

## TL;DR
A user story states one requirement from a user's point of view: **As a `<role>`, I want to `<goal>` so that `<benefit>`.** Read its nouns to find candidate objects and its verbs to find responsibilities and connections; what the sentence leaves unsaid becomes your next questions.

## The three slots
| Slot | Content | Check |
|---|---|---|
| As a … | The user role | A real role, not "user" when several roles behave differently |
| I want to … | The goal the role wants to reach | A goal, not a UI instruction ("click the blue button") |
| so that … | Why it matters | May be dropped only when obvious; usually it is what lets you judge alternatives |

## From story to design
Story: *As an online shopper, I want to add an item to my shopping cart, so that I can purchase it.*

| Reading | Finds | Here |
|---|---|---|
| Nouns | Candidate objects | Shopper, Item, Shopping cart |
| Verbs | Responsibilities | Cart: add item; purchase |
| Verbs linking nouns | Connections | Shopper *has* a cart; cart *holds* items |
| What is missing | Follow-up questions | Can an item be added twice? Is stock checked? Does the cart persist between sessions? |

Take the result straight to CRC cards.

## Quality check (INVEST)
Independent · Negotiable · Valuable · Estimable · Small · Testable. The two that fail most often:
- **Small:** "and" in the goal usually means two stories.
- **Testable:** no acceptance criteria means nobody can say when it is done.

## Acceptance criteria
Attach concrete, checkable conditions to each story, ideally `Given / When / Then` with real values, covering at least one normal case, one edge case and one rejection case.

```
Given a cart containing 1 unit of item A and stock of A is 1
When the shopper adds another unit of A
Then the cart still shows 1 unit and a "not enough stock" message appears
```

## Common mistakes
- Role is a system component ("As the database…").
- Story describes a solution, removing room to negotiate.
- Stories written per screen instead of per goal.
- Technical work disguised as a story with no user benefit; track it as a task under the story it enables.

---
*Source: Summary in our own words of the short reading *Expressing Requirements with User Stories* (University of Alberta, Object-Oriented Design course), extended with common practice (INVEST, acceptance criteria). Not a verbatim copy.*
