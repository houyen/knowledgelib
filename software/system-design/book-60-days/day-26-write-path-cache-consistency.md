---
id: software/system-design/book-60-days/day-26-write-path-cache-consistency
canonical_question: Write-Path Cache Consistency
aliases:
- System Design Day 26
- Write-Path Cache Consistency
- Day 26 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 26: Write-Path Cache Consistency

DAY 26 · SYSTEM DESIGN
Write-Path Cache Consistency
Your cache and DB are out of sync. Again.
A user updates their profile. The cache still serves the old name for the next 10 minutes. Support gets a
ticket. You patch it with a cache flush. It happens again next week.
You're asked to fix write consistency before it becomes a customer-facing incident.
Here's the setup:
NestJS API →  PostgreSQL (source of truth) + Redis (cache)
~600 req/s reads, ~80 req/s writes at peak
Current pattern: write to DB, manually invalidate cache key on success
3 incidents this month — all traced back to stale cache after writes
You need a strategy that survives race conditions, retries, and partial failures
What do you change?
A Write-through — write to cache and DB together, synchronously. Cache is always warm, always
consistent.

---

DAY 26 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Dual-write with an outbox
The core problem isn't "which order to write in" — it's "what happens when one write succeeds and
the other fails?"
Why D wins: Every naive dual-write has the same race condition: write to DB, write to cache, crash
between the two →  stale cache indefinitely. The outbox makes the cache update a consequence of the
DB write, not a sibling operation. One atomic DB transaction: record + outbox event. A consumer
updates Redis from the event. Also gives you replay — if Redis goes down and comes back, re-process
the outbox.
Answer 2
Why A fails (Write-through): Looks safest. Is the most dangerous at scale. Two synchronous I/Os on
every write. If Redis is slow, your write API is slow. If Redis is down, do you block the user? You've
made Redis a hard dependency of your write path.
