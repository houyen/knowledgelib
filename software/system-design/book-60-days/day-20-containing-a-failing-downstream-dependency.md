---
id: software/system-design/book-60-days/day-20-containing-a-failing-downstream-dependency
canonical_question: Containing a Failing Downstream Dependency
aliases:
- System Design Day 20
- Containing a Failing Downstream Dependency
- Day 20 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 20: Containing a Failing Downstream Dependency

DAY 20 · SYSTEM DESIGN
Containing a Failing Downstream Dependency
Your checkout service calls a 3rd-party fraud-check API on every order.
That API just started timing out at 30s instead of its usual 200ms.
Your Node.js checkout pods have a 50-connection pool. Within 90 seconds, every connection is parked
waiting on the fraud API. New checkout requests pile up in the queue. P99 latency on /checkout goes from
300ms to 28s. Customers retry. Pods OOM. The fraud API is degraded — your entire checkout is down.
Here's the setup:
• Checkout (NestJS) →  Fraud API (3rd party) — 30s timeouts
• Same pods also handle /cart, /orders, /health — all healthy dependencies
• Fraud API's own dashboard says it'll be back in ~10 minutes
• Your SLO budget for the quarter is about to evaporate
You need to stop the bleeding without losing the rest of checkout. What do you do?
A Drop the timeout to 2s and add 3 retries with exponential backoff.

---

DAY 20 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Circuit Breaker + Bulkhead, together ✅
Here's why, and why the other three trick smart engineers:
Why D wins (Circuit Breaker + Bulkhead):
These two patterns solve two different failure modes, and you need both.
The Circuit Breaker stops you from hammering a dead dependency. After N consecutive failures (or a
failure rate threshold over a rolling window), it flips to OPEN — every subsequent call to the fraud
API fails instantly with a fallback. No 30s wait. No connection held hostage. After a cooldown (say
30s), it goes HALF-OPEN: it allows exactly one probe request through. If that probe succeeds, the
breaker closes and traffic resumes. If it fails, back to OPEN for another cooldown. Half-open is the
part most tutorials gloss over — it's what prevents the thundering herd from re-killing a service that's
just coming back up.
The Bulkhead is the part most engineers forget exists until they get burned. It isolates resource pools.
Your fraud API gets its own dedicated pool of, say, 10 connections — separate from the 40 connections
that serve /cart, /orders, /health. When the fraud API hangs, it can saturate its 10 connections, but
