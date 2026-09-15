---
id: software/system-design/book-60-days/day-09-splitting-read-and-write-data-models
canonical_question: Splitting Read and Write Data Models
aliases:
- System Design Day 09
- Splitting Read and Write Data Models
- Day 09 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 09: Splitting Read and Write Data Models

DAY 09 · SYSTEM DESIGN
Splitting Read and Write Data Models
Your orders service is a Postgres monolith doing 8K writes/min and 40K reads/min.
Same tables. Same schema. Everything's grinding.
The write side needs a normalized schema — orders, line_items, payments, shipments, addresses. Clean
FKs, ACID, no duplicated data. The read side wants the opposite — the dashboard joins 7 tables to render
one order card, and the reporting queries are lighting up the CPU at 85% every morning at 9am.
You've already tuned indexes. You've already added caching. The fundamental problem isn't hardware —
the read model and the write model want different shapes of the same data, and you've been pretending
they're the same thing for two years.
Here's the decision on the table:
A Full CQRS — separate read/write models, project writes into a denormalized read store
(ElasticSearch / a flat Postgres read DB), eventual consistency between them.
B Add read replicas — point dashboards + reports at the replica, keep writes on the primary.

---

DAY 09 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
✅  Answer: A — Full CQRS
Why A wins:
The pain isn't "reads are slow" — it's that the write side wants a normalized schema and the read side
wants a denormalized one, and you're forcing them to share. No amount of hardware fixes a schema
shape mismatch. Write side stays clean: orders, line_items, payments, all normalized, ACID, FK-
enforced. Read side is a projection: a flat order_view table (or Elasticsearch index) where every order
card renders from one row, zero joins. Projector keeps them in sync (outbox →  Kafka →  read-model
updater, or CDC). You eat eventual consistency — the dashboard might lag by a few hundred ms. For
95% of reads (dashboards, reports, search), that's invisible. For the 5% that needs strong consistency
(user's own order confirmation), read from the write side directly.
Answer 2
Why B is the trap (Read replicas):
B fixes read load. Not read shape. The 7-table join is still a 7-table join — it just runs on different
hardware. You've moved the CPU bill, not removed it. Latency drops for 6 months while traffic grows,
then you're back where you started with 3 replicas all running the same expensive joins. B is right
when the joins are structurally fine but the primary is overwhelmed. Wrong when the joins themselves
are the problem.
