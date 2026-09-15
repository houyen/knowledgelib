---
id: software/system-design/book-60-days/day-08-keeping-cache-and-database-in-sync
canonical_question: Keeping Cache and Database in Sync
aliases:
- System Design Day 08
- Keeping Cache and Database in Sync
- Day 08 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 08: Keeping Cache and Database in Sync

DAY 08 · SYSTEM DESIGN
Keeping Cache and Database in Sync
E-commerce product catalog. Redis in front of Postgres. 40K RPS at peak.
In staging, cache hit ratio sits at 94%. Response times under 20ms. Everything looks clean.
Ship to prod. Within 48 hours, support tickets start rolling in. Customers seeing wrong prices. Old stock
counts. Products showing "available" that shipped out three hours ago.
Here's the setup:
App (Node.js) →  Redis (cache) →  Postgres (source of truth)
Writes come from: admin panel (price updates), inventory service (stock decrements), order service
(purchase events).
Reads come from: product pages, search results, checkout flow.
The cache is leaking stale data in production. Your team is debating the invalidation strategy. What do you
ship?
A Write-through — every write hits cache and Postgres in the same transaction. Cache is never
stale.

---

DAY 08 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
✅  Answer: C — Cache-aside
Why C wins:
Multiple write paths (admin panel, inventory service, order service) all hit Postgres independently.
Cache-aside fits perfectly: each writer updates Postgres →  invalidates the cache key (DEL
product:123) →  next read misses →  fetches fresh data →  repopulates Redis. Postgres stays the
uncontested source of truth. Redis is just a disposable read accelerator. If Redis dies, the app still
works — slower, but correct. This is what Shopify, Etsy, and most AWS reference architectures run in
prod.
Answer 2
Why A is the trap (Write-through):
"We write to both atomically" — except there's no distributed transaction between Redis and Postgres.
You write to Postgres, then write to Redis. If the Redis write fails (network blip, timeout), you have
consistent Postgres + stale Redis. The exact bug you were trying to fix. Worse, write-through couples
every service to Redis — now your inventory service and order service both need Redis credentials.
One Redis outage takes down your entire write path. Works great for single-service/single-writer
systems. Falls apart with multiple writers.
