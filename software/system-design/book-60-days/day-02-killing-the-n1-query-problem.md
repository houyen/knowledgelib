---
id: software/system-design/book-60-days/day-02-killing-the-n1-query-problem
canonical_question: Killing the N+1 Query Problem
aliases:
- System Design Day 02
- Killing the N+1 Query Problem
- Day 02 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 02: Killing the N+1 Query Problem

DAY 02 · SYSTEM DESIGN
Killing the N+1 Query Problem
Your /orders endpoint loads 50 orders on a page.
P95 is 2.4s. The DB's fine. The app server's fine. Nothing's on fire.
Then you open the query log.
51 queries per request. One SELECT for the orders list. Then 50 more — one per order — to fetch the
customer. The ORM is doing lazy-load on order.customer inside your map.
Classic N+1. You've seen it before. The fix is "obvious" — until the team meeting, where three engineers
propose three different things and everyone thinks they're right.
Here's what's on the table:
A Eager-load the relation — include: { customer: true } on the Prisma query. One JOIN, done.
B Add a DataLoader in front of the customer lookup — batches the 50 IDs into one WHERE id IN
(...) behind the scenes.
C Cache the customer by ID in Redis — every lookup hits cache first, DB only on miss.

---

DAY 02 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins: One LEFT JOIN customers ON orders.customer_id = customers.id returns the whole
page in a single round trip. P95 drops from 2.4s to ~80ms. No new infrastructure. No new failure
modes. The N+1 problem in an ORM almost always has the same root cause: a lazy relation the
developer didn't realize was lazy. Prisma's include, Sequelize's include, TypeORM's relations — every
ORM has this. Reach for fancier patterns only when JOIN genuinely can't solve it.
Answer 2
Why B is the trap (DataLoader): Beautiful pattern — but earns its keep in GraphQL where the
resolver graph fans out in ways a single JOIN can't express. Here you have one list endpoint with one
relation. A JOIN is strictly simpler and strictly faster. You're solving a problem you don't have and
paying the complexity tax forever.
