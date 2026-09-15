---
id: software/system-design/book-60-days/day-06-safe-distributed-locks-for-cron-jobs
canonical_question: Safe Distributed Locks for Cron Jobs
aliases:
- System Design Day 06
- Safe Distributed Locks for Cron Jobs
- Day 06 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 06: Safe Distributed Locks for Cron Jobs

DAY 06 · SYSTEM DESIGN
Safe Distributed Locks for Cron Jobs
Your job scheduler runs on 3 instances behind an ALB.
Every 5 minutes, a cron fires the same "generate-daily-report" job — and all 3 instances try to grab it.
You reach for the classic fix: a Redis SETNX lock.
SET job:daily-report locked NX EX 300 →  only one instance wins. Done.
Works perfectly for a month. Until 2am on a Saturday.
Instance B wins the lock. Starts the job. 60 seconds in, the pod gets OOM-killed. The lock is still there. TTL
says 300 seconds. The report runs once every 5 minutes.
Nothing processes that report for 4 more minutes. Then instance A grabs it — but instance B's pod restarted
and it's ALSO trying to run it now. Both instances processing the same job.
Worse: a slow GC pause on instance A makes it hold the lock past TTL. Redis quietly hands the lock to
instance C. Now A thinks it owns the lock. C also thinks it owns the lock. Both write to the same output.
What's the right pattern here?

---

DAY 06 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: A — SETNX + short TTL + fencing token ✅
Here's why, and why the other three trick smart engineers:
Why A wins (SETNX + TTL + fencing token):
A lock alone can't protect a distributed resource. You need to assume the lock holder might be dead,
paused, or partitioned — and the lock might get reassigned while they still think they own it. This is
exactly the scenario above: GC pause, TTL expires, Redis gives the lock to someone else, original
owner wakes up and keeps writing.
The fencing token fixes it. Every time a lock is acquired, Redis (or the lock service) hands out a
monotonically increasing number — 42, 43, 44. The downstream resource (the DB, the storage
system, the output queue) remembers the highest token it's seen and rejects any write with a lower
token.
So when instance A wakes up from its GC pause holding token 42, and instance C is already writing
with token 43, A's write gets rejected by the DB itself. The resource is the source of truth — not the
lock service.
