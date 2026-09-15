---
id: software/system-design/book-60-days/day-18-surviving-a-cache-stampede
canonical_question: Surviving a Cache Stampede
aliases:
- System Design Day 18
- Surviving a Cache Stampede
- Day 18 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 18: Surviving a Cache Stampede

DAY 18 · SYSTEM DESIGN
Surviving a Cache Stampede
Your Redis cache just expired on a key that 8,000 users hit every second.
Every single one of those requests is now flying straight at your database.
This is the thundering herd. You didn't have a traffic problem — you had a cache problem. Now you have
both.
Here's the setup:
Service →  Node.js API, 8,000 req/sec on the /feed endpoint
Cache →  Redis, TTL = 60s on the feed key
DB →  Postgres, comfortable at ~200 req/sec sustained
What happened →  TTL expired at peak traffic, all 8,000 req/sec hit Postgres simultaneously
The DB is on its knees. You have minutes before it falls over. And the next TTL expiry is in 60 seconds.
What do you do?
A Mutex lock — only one request queries the DB to rebuild the cache, the rest wait behind it.

---

DAY 18 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Cache pre-warming ✅
Here's why, and why the other three trick smart engineers:
Why D wins (Cache pre-warming):
Pre-warming eliminates the thundering herd at the root. A background job — a cron, a scheduled
Lambda, a Sidekiq worker — rebuilds the cache key on a fixed schedule that's shorter than the TTL.
The key never goes cold in production. There's no expiry cliff for 8,000 requests to fall off.
You know the data is hot. You know when it expires. You have the compute to rebuild it proactively.
The cost is a background job running every ~45 seconds; the benefit is your database never sees the
spike. Netflix pre-warms content metadata. Twitter pre-builds timelines for high-follower accounts.
The pattern is everywhere — it's just not glamorous enough to make it into most architecture posts.
One detail that matters: pair it with stale-while-revalidate. Serve the stale value while the background
job refreshes, so a slightly-late rebuild never causes a miss.
