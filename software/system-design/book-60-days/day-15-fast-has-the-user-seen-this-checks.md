---
id: software/system-design/book-60-days/day-15-fast-has-the-user-seen-this-checks
canonical_question: Fast Has the User Seen This Checks
aliases:
- System Design Day 15
- Fast Has the User Seen This Checks
- Day 15 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 15: Fast Has the User Seen This Checks

DAY 15 · SYSTEM DESIGN
Fast “Has the User Seen This?” Checks
You're running a content recommendation feed. 50M users.
Every API call asks: "has this user already seen post X?"
Right now you're hitting Postgres on every check. The user_seen_posts table has 80B rows and growing.
p99 latency on the feed endpoint just crossed 600ms and your DBA is sending you screenshots of CPU
graphs at 2am.
Here's the setup:
• Feed service: Node.js, ~120K RPS at peak
• "Already seen" check: SELECT against Postgres on every recommendation
• Table: user_seen_posts(user_id, post_id, seen_at) (partitioned, indexed, still slow)
• Cache hit ratio is fine. The problem is the long tail of cold lookups
• False positives on "already seen" are tolerable. False negatives (showing the same post twice) are not
great but survivable
Product wants p99 under 100ms. You have one sprint. What do you do?

---

DAY 15 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
◧  Author's diagram unavailable (source image returned 404)
A — Bloom Filter per user in Redis (THE RIGHT ANSWER)
Bloom filters give one ironclad guarantee: "this item is DEFINITELY NOT in the set." If the filter says no
→  skip Postgres entirely. If it says maybe →  fall through to confirm.
Why it wins here:
• ~97% of feed checks are for posts the user has never seen →  sub-millisecond "definitely no" from
Redis, Postgres never touched
• Memory math: 10K posts per user in a Bloom filter at 1% false-positive = 12 KB. Same data as a
Redis SET = 80 KB+, and grows linearly
• At 50M users: Bloom filter = ~600 GB. Redis SET = ~4 TB. That's the difference
• Real-world users: Medium's "have you read this", Cassandra's SSTable short-circuit, Bitcoin's SPV
wallets
The 1% false positive here means you occasionally skip showing a post the user hasn't seen. Product
said that's tolerable. Bloom filters never produce false negatives (showing the same post twice) —
which would be the dealbreaker.
Answer 2
B — Redis SET per user (SENIOR ENGINEER TRAP)
Looks strictly better on paper — same O(1) speed, plus perfect accuracy, no false positives.
SISMEMBER is battle-tested.
The trap: memory explodes on power users. A user with 50K posts seen = 3–4 MB in a Redis SET.
Your top 5% users blow up the Redis cluster. You'll either over-provision (expensive) or start evicting
hot users (defeats the whole point).
Rule of thumb: Redis SET when cardinality is small (<1K per key) or false positives are unacceptable.
Bloom filter when cardinality is large and "probably not" is good enough.
