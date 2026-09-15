---
id: software/system-design/book-60-days/day-33-reconstructing-state-with-event-sourcing
canonical_question: Reconstructing State with Event Sourcing
aliases:
- System Design Day 33
- Reconstructing State with Event Sourcing
- Day 33 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 33: Reconstructing State with Event Sourcing

DAY 33 · SYSTEM DESIGN
Reconstructing State with Event Sourcing
Your order service takes 200 writes/sec at peak.
You audit 6 months of data. Something's off — two orders show the same ID, different totals.
You have the current state. You don't have how it got there.
Your DB is a graveyard of overwritten rows.
Here's the system:
• OrderService →  Postgres (current state only)
• Events: placed, updated, cancelled, refunded
• Every UPDATE overwrites the previous row
• No audit log. No event history. No replay.
A billing dispute just landed. You need to reconstruct exactly what happened to Order #8471. You can't.
Instead of storing the current state, you store the sequence of events that produced it.
What's your approach when redesigning this service?

---

DAY 33 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: A — Event Sourcing ✅
Here's why, and why the other three look reasonable but miss the point:
Why A wins (Event Sourcing):
Event Sourcing flips the model entirely. Instead of storing the latest state and losing how you got
there, you store every event that ever happened. The current state is a projection — computed by
replaying events from the beginning (or from a snapshot).
For Order #8471: you don't query a row. You replay OrderPlaced, OrderUpdated, PaymentCaptured,
RefundInitiated. Every mutation is preserved, timestamped, immutable. You can reconstruct state at
any point in time. You can build new projections (e.g., "total revenue by SKU last 90 days") without
changing the core model — just replay and project differently.
This is what Axon, EventStoreDB, and the event-sourced layers in most serious fintech/e-commerce
systems do. It's not a log — it's the primary data model.
