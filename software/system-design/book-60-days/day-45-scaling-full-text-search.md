---
id: software/system-design/book-60-days/day-45-scaling-full-text-search
canonical_question: Scaling Full-Text Search
aliases:
- System Design Day 45
- Scaling Full-Text Search
- Day 45 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 45: Scaling Full-Text Search

DAY 45 · SYSTEM DESIGN
Scaling Full-Text Search
Your search box returns results in 80ms.
Then you add 50M more documents. Now it's 4 seconds.
Your DBA says "add an index." Your search engineer says "that's not how this works."
They're both right — about different things.
Here's the setup:
Platform: SaaS product, 100M documents
Search fields: title, description, tags, partial phrases
Current stack: PostgreSQL full-text search
Current perf: p95 = 4.2s
Target: sub-200ms at p99
Product is escalating. What do you do?
A Migrate to Elasticsearch — inverted index, purpose-built for full-text, sub-100ms at scale.

---

DAY 45 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins (Elasticsearch):
Elasticsearch is built on an inverted index. When you index a document, Elasticsearch tokenizes the
text and writes posting lists: "database" →  [doc_1, doc_5, doc_23...], "index" →  [doc_2, doc_5,
doc_18...]. A query for "database index" does a fast posting-list intersection — not a table scan.
At 100M documents, that intersection still runs in milliseconds because posting lists are stored in
delta-compressed sorted form, Lucene segments are immutable (no row locking, no MVCC overhead),
horizontal sharding is native (queries fan out in parallel), and BM25 scoring runs during retrieval —
not after it.
Result: sub-100ms at p99, even at 100M+ docs, with proper shard sizing. Netflix, Uber, and GitHub
all run some form of this at their search layer.
The tradeoffs you accept: new infrastructure to operate (index lifecycle, shard rebalancing), write
amplification from segment merging, and eventual consistency — by default, newly indexed docs
aren't searchable for ~1 second.
