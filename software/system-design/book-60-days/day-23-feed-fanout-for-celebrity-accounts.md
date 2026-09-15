---
id: software/system-design/book-60-days/day-23-feed-fanout-for-celebrity-accounts
canonical_question: Feed Fanout for Celebrity Accounts
aliases:
- System Design Day 23
- Feed Fanout for Celebrity Accounts
- Day 23 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 23: Feed Fanout for Celebrity Accounts

DAY 23 · SYSTEM DESIGN
Feed Fanout for Celebrity Accounts
Your feed service was reading at 20ms.
Then a celebrity with 2M followers posted.
Now you're at 4 seconds. P99 is on fire.
Here's the setup:
10M users. ~50k posts/day. One account: 2M followers.
Every time that account posts, your feed query fans out across 2M follower rows, sorts by timestamp, and
buries your read replicas.
Your team is debating how to fix the delivery model — not the query, the architecture.
A) Fanout on Write — push to every follower's cache on post. Reads instant. Celebrity post = 2M cache
writes.
B) Fanout on Read — no precomputation. Fetch + merge at read time. Simple writes. Painful at scale.
C) Hybrid fanout — fanout on write for regular users, fanout on read for celebrities. Merge at read time
only for the celebrity slice.

---

DAY 23 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: C — Hybrid fanout
Why C wins:
This is how Twitter actually solved it — they published the architecture. The insight: fanout-on-write
is fast for readers but catastrophic for high-follower accounts. Fanout-on-read is simple but destroys
latency at scale. Hybrid is honest about both failure modes.
When a post is created →  check follower count. Under 10k? Fan out immediately to all followers'
Redis feed caches. Over 10k (celebrity)? Skip the fanout. At read time, fetch from two sources:
precomputed cache (regular accounts) + real-time query for celebrity accounts. Merge + deduplicate.
The celebrity slice is small and bounded. Result: P99 stays fast, no 2M synchronous writes on celebrity
posts.
