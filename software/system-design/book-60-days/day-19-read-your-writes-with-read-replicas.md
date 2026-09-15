---
id: software/system-design/book-60-days/day-19-read-your-writes-with-read-replicas
canonical_question: Read-Your-Writes with Read Replicas
aliases:
- System Design Day 19
- Read-Your-Writes with Read Replicas
- Day 19 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 19: Read-Your-Writes with Read Replicas

DAY 19 · SYSTEM DESIGN
Read-Your-Writes with Read Replicas
Your checkout endpoint has a 400ms P95. Profiling shows 70% of that is DB reads.
You add a read replica and point all SELECT queries at it. P95 drops to 90ms. The team celebrates.
Two hours later, support tickets flood in. Customers update their shipping address but see the old one on
the confirmation screen. One customer gets charged twice because the "order already exists" check read
stale data and missed the duplicate.
Here's the setup:
• Primary →  handles all writes, replication lag ~200ms
• Replica →  handling 100% of reads
• Affected flows →  profile updates, order dedup, payment idempotency
The replica is working exactly as designed. That's the problem.
What do you do?
A Read-your-writes consistency: route a user's reads to primary for a short window after they write.

---

DAY 19 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins:
After a user performs a write, their subsequent reads are routed to the primary for a short window:
typically a few seconds, or until replica lag catches up. Everyone else reads from the replica. The
performance win is preserved for the vast majority of traffic.
Answer 2
Why D is the trap:
"Critical" is not a stable category. The primary read list quietly shrinks, stale read bugs come back, and
you spend the next quarter playing whack-a-mole with consistency bugs. You've traded a systematic
solution for a per-feature judgment call.
