---
id: software/system-design/book-60-days/day-57-consistency-for-payment-confirmation-reads
canonical_question: Consistency for Payment-Confirmation Reads
aliases:
- System Design Day 57
- Consistency for Payment-Confirmation Reads
- Day 57 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 57: Consistency for Payment-Confirmation Reads

DAY 57 · SYSTEM DESIGN
Consistency for Payment-Confirmation Reads
Your write traffic just hit 50k writes/sec. Reads are 10x that.
You split your Postgres into one primary + two replicas. Reads go to replicas. Now you're shipping a
payment confirmation flow — and a replica returned stale data 200ms after a write. The user saw
"payment pending" when it already succeeded.
Here's the setup:
→  Primary handles all writes
→  Two read replicas, async replication
→  Payment confirmation reads from a replica
→  Replication lag: 80–300ms under load
You need reads-after-write consistency on payment flows without tanking write throughput. What do you
do?
A Switch to synchronous replication — primary waits for at least one replica to confirm before
ack'ing the write.

---

DAY 57 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why C wins (primary reads for critical paths):
Payment confirmations are a tiny slice of your read traffic. You're not routing ALL reads to primary —
just the reads where stale data causes visible user harm.
This pattern is called read-your-writes consistency. Stripe, Shopify, every serious fintech does this.
You add a flag or middleware: "if this is a consistency-sensitive flow, read from primary." Everything
else keeps hitting replicas.
Primary read traffic increases slightly — but a "just confirmed payment" flow is maybe 0.1% of your
reads. Negligible. No topology change, no new failure modes, surgical precision.
