---
id: software/system-design/book-60-days/day-05-choosing-a-database-sharding-strategy
canonical_question: Choosing a Database Sharding Strategy
aliases:
- System Design Day 05
- Choosing a Database Sharding Strategy
- Day 05 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 05: Choosing a Database Sharding Strategy

DAY 05 · SYSTEM DESIGN
Choosing a Database Sharding Strategy
4 database sharding strategies. 4 completely different scaling outcomes. One wrong choice and you're
melting a primary on Black Friday.
Your Postgres orders table just crossed 500M rows.
Range scans that used to take 40ms are creeping past 800ms.
Vertical scaling is dead. You need to shard.
Here is the workload:
• orders = 500M rows, growing 3M/week
• 80% reads = "customer X's last 30 days of orders"
• 15% reads = analytics joins on date ranges
• 5% writes = new orders (steady 400 RPS, 2x on sale days)
Which strategy do you pick?
A Hash sharding on order_id — even distribution, no hotspots.

---

DAY 05 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: C — Directory-based sharding ✅
Here is why the other three trick smart engineers:
Why C wins (Directory-based):
80% of reads are "customer X's orders." You want every order for a customer on exactly one shard. A
customer-scoped read hits one node, no scatter-gather fan-out.
You keep a customer_shard_map table (cached in Redis). If shard 3 gets hot, you migrate specific
heavy customers (whales) without rehashing anything. Targeted rebalancing is the superpower.
Figma, Notion, and Slack do this.
Answer 2
Why A is the trap (Hash on order_id):
The classic tutorial answer: "Hash the primary key!" It wrecks you here. A single customer's 200 orders
scatter across all shards. Every read becomes a 4-shard fan-out gated by your slowest node. P99
latency goes up.
Answer 3
Why B is wrong (Range on created_at):
Creates a hot shard by design. Every new order writes to the same shard. Your newest shard absorbs
100% of writes and 70% of reads. On Black Friday, this shard melts while others sit idle.
Answer 4
Why D is wrong (Consistent hashing):
Great for uniform data, but you can't migrate specific heavy tenants. If four whales land on the same
shard, you are stuck.
