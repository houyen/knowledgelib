---
id: software/system-design/book-60-days/day-47-incrementally-strangling-a-monolith
canonical_question: Incrementally Strangling a Monolith
aliases:
- System Design Day 47
- Incrementally Strangling a Monolith
- Day 47 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 47: Incrementally Strangling a Monolith

DAY 47 · SYSTEM DESIGN
Incrementally Strangling a Monolith
Your monolith is 6 years old.
500k lines of code. One deploy every 3 weeks. One bad migration takes down the whole thing.
Leadership says: "rewrite it." You've seen what happens when teams do that. 18 months. Budget overruns.
Half the features never make it back. The new system launches and nobody trusts it.
There's a better way. You don't rewrite — you strangle.
Here's your system:
• OrderService (monolith) handles: order creation, fulfillment, invoicing, returns
• 40 engineers. 3 teams. All deploying to the same codebase.
• Returns processing is a bottleneck. The business wants it extracted first.
• You can't freeze feature work during migration.
You need to extract Returns into a standalone service without a big-bang rewrite.
What's your migration strategy?

---

DAY 47 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins:
You introduce a routing proxy in front of the monolith. /returns traffic routes to the new service. The
monolith handles everything else. You run both in parallel — no freeze, no big-bang. Migrate one
endpoint at a time, each step independently rollback-able. Only deprecate monolith code after the
new service has proven itself under real load. Netflix and Amazon have run versions of this at scale.
Answer 2
Why B is close but different (Branch by Abstraction):
Real pattern — but it lives inside the codebase. You wrap the logic behind an interface, build the new
implementation behind a flag, then flip it. It's a refactoring tool, not a deployment strategy. Often used
inside a Strangler Fig migration to prepare internal structure. But on its own it doesn't get you to an
independently deployed service.
