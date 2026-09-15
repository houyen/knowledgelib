---
id: software/system-design/book-60-days/day-16-taming-a-hot-partition-key
canonical_question: Taming a Hot Partition Key
aliases:
- System Design Day 16
- Taming a Hot Partition Key
- Day 16 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 16: Taming a Hot Partition Key

DAY 16 · SYSTEM DESIGN
Taming a Hot Partition Key
You're running a multi-tenant analytics pipeline on DynamoDB. 200 tenants, 12K writes/sec total.
Everything is fine — until it isn't.
One tenant onboards a massive customer overnight. Their event volume 100x's. Now that one tenant is
hitting 9K writes/sec on a single partition key. The other 199 tenants sit idle.
ProvisionedThroughputExceeded errors start firing. P99 write latency spikes from 8ms to 400ms. Your on-
call gets paged. Everyone is getting throttled because of one key.
Here's the setup:
• Table: events (DynamoDB, on-demand capacity)
• PK: tenant_id · SK: event_timestamp
• Hot tenant: ~9K WPS · All other tenants: ~15 WPS each
• Single partition key absorbing all 9K writes — DynamoDB's per-partition limit is the wall
Classic hot partition. What do you do?
A Write sharding — append a random suffix to the PK (tenant_id#0 … tenant_id#9).

---

DAY 16 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
A — Write Sharding (THE RIGHT ANSWER)
DynamoDB hashes the partition key to decide which physical shard handles the write. One PK value =
one shard = one wall. When that tenant hits 9K WPS, the shard caps out.
The fix: append a random suffix at write time — tenant_id#0 through tenant_id#9. Now the hash
function sees 10 different keys and distributes writes across 10 logical partitions (~900 WPS each,
well under the limit). Throttling stops, P99 drops back to single digits.
The read cost: scatter-gather across all 10 suffixes to query that tenant's data. For a write-heavy
analytics pipeline, that's the right tradeoff.
This is literally the pattern AWS documents as the canonical fix for hot partitions.
