---
id: software/system-design/book-60-days/day-14-safely-rolling-out-a-risky-change
canonical_question: Safely Rolling Out a Risky Change
aliases:
- System Design Day 14
- Safely Rolling Out a Risky Change
- Day 14 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 14: Safely Rolling Out a Risky Change

DAY 14 · SYSTEM DESIGN
Safely Rolling Out a Risky Change
You're shipping a rewrite of your checkout write path on Friday.
Node.js on ECS Fargate. ~3,000 RPS at peak. Postgres with row-level locking on the orders table. The
change touches the line of code that actually charges the customer's card — old path uses Stripe Charges
API, new path uses PaymentIntents with 3DS.
The QA env is green. Load test passed. Your staff engineer signs off.
But it's checkout. If this breaks, money breaks. And you can't roll back a card that already got charged.
Pick the deploy strategy:
A Blue/Green — spin up a parallel "green" environment running the new code, smoke-test it, flip
the load balancer. Instant rollback by flipping back.
B Canary — route 1% of live traffic to the new version, watch error rates and p99 latency for 30
minutes, then ramp 5% →  25% →  100%.

---

DAY 14 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Feature Flag ✅
Here's why, and why the other three look right but quietly fail when the change touches money:
Why D wins (Feature Flag):
Feature flags decouple deploy from release. The new code ships to 100% of your ECS tasks — but it's
dormant. Nothing executes until you flip the flag.
• Rollback is a config push, not a deploy. Sub-second. No ECS restarts, no LB drain, no DNS TTL.
• You target who sees the new path, not what % of random traffic. $0.99 customer and $40K B2B
customer shouldn't get coin-flipped equally — that's not a strategy, that's hope.
• You can keep the old code path warm for weeks. 3DS edge case on a specific issuing bank in
Brazil? Flip those users back while keeping everyone else on v2.
