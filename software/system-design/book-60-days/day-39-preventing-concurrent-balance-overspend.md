---
id: software/system-design/book-60-days/day-39-preventing-concurrent-balance-overspend
canonical_question: Preventing Concurrent Balance Overspend
aliases:
- System Design Day 39
- Preventing Concurrent Balance Overspend
- Day 39 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 39: Preventing Concurrent Balance Overspend

DAY 39 · SYSTEM DESIGN
Preventing Concurrent Balance Overspend
You have a payment system. Two users try to spend from the same wallet balance at the same time.
Both read $200. Both want to spend $150. Both see enough balance. Both write the deduction.
The wallet is now at -$100. How do you stop this?
A Pessimistic locking — SELECT FOR UPDATE on the wallet row. One transaction blocks until the
other commits.
B Optimistic locking — read the row with a version number, only write if version hasn't changed
since you read it. Retry on conflict.
C MVCC — let both reads see a consistent snapshot, rely on the database to detect write conflicts at
commit time.
D Serializable isolation — set the transaction isolation level to SERIALIZABLE and let the database
handle it.

---

DAY 39 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins (optimistic locking):
You read the wallet row, grab the version number. When you write, you include a WHERE version =
:read_version condition. If another transaction already updated the row, your WHERE matches zero
rows — conflict detected, retry.
UPDATE wallets
SET balance = balance - 150, version = version + 1
WHERE id = :wallet_id AND version = :read_version;
If rows_affected = 0 →  conflict →  retry. No locks held during the read. At 10K TPS with low conflict
rates, this is significantly faster than pessimistic locking — you're only paying for retry cost on actual
conflicts, not lock acquisition on every read.
The catch: under HIGH contention (same hot wallet hit repeatedly), retry storms eat you alive. Hot
wallets need Redis INCRBY with atomic decrement, or a queue in front of the wallet update.
