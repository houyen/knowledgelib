---
id: software/system-design/book-60-days/day-12-indexing-a-high-ingest-table
canonical_question: Indexing a High-Ingest Table
aliases:
- System Design Day 12
- Indexing a High-Ingest Table
- Day 12 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 12: Indexing a High-Ingest Table

DAY 12 · SYSTEM DESIGN
Indexing a High-Ingest Table
Your events table on PostgreSQL 15 just crossed 200M rows.
Ingestion runs at 8K writes/sec from a Kafka consumer. P99 write latency was 12ms — now it's 140ms and
climbing.
The dashboard team is screaming. Their query filters on (tenant_id, event_type, created_at) and scans 40M
rows per request. They want an index. Yesterday.
You check pg_stat_user_indexes. The table already has 4 indexes. Each new write touches every one of
them. Add a fifth and your ingestion lag becomes ingestion failure.
But 92% of dashboard queries hit a single tenant's last 7 days of signup events. A tiny slice of a huge table.
What do you do?
A) Add a composite B-tree on (tenant_id, event_type, created_at). Standard answer, covers the query, done.
B) Add a covering index with INCLUDE (user_id, payload) so the query never hits the heap. Index-only
scan.
C) Stop adding indexes to the primary. Spin up a read replica and route the dashboard there. Keep writes
lean.

---

DAY 12 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Partial Index ✅
Here's why, and why the other three trick smart engineers.
Why D wins (Partial Index)
92% of your queries hit one tenant's last 7 days of signup events. A partial index only indexes rows
that match its WHERE clause — everything else writes to the table without touching this index at all.
The math: if signup events are ~4% of the stream and the 7-day window covers ~5% of the table,
your partial index covers roughly 0.2% of rows. Inserts that don't match the predicate cost you
nothing on this index. The write amplification is almost entirely gone.
PostgreSQL's planner uses the partial index for any query whose WHERE clause is a subset of the
index predicate. Your dashboard query gets full coverage. Reads stay fast, writes stay alive.
The catch: when the dashboard team wants 30 days instead of 7, you rebuild. That's a known cost,
not a hidden one.
