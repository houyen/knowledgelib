---
id: software/system-design/book-60-days/day-28-choosing-a-vector-store-for-semantic-search
canonical_question: Choosing a Vector Store for Semantic Search
aliases:
- System Design Day 28
- Choosing a Vector Store for Semantic Search
- Day 28 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 28: Choosing a Vector Store for Semantic Search

DAY 28 · SYSTEM DESIGN
Choosing a Vector Store for Semantic Search
You're building a semantic search feature for a B2B SaaS product.
The corpus: 4 million support articles, docs, and user-generated tickets. Users type natural language
queries. They expect Google-quality results — not keyword matching.
Your current stack: PostgreSQL 15, Redis, and a Node.js backend. The search team says ILIKE and pg_trgm
aren't cutting it. Embeddings are the answer. Now you need a place to store and query 1536-dimensional
vectors (OpenAI ada-002) at <100ms p99.
4 million rows. ~24GB of raw embeddings. Query volume: 300 req/s with weekend spikes to 900 req/s.
Where do you store and query those vectors?
A pgvector extension on your existing PostgreSQL — store embeddings in a new column, query
with <-> cosine similarity.
B Pinecone — fully managed vector database, serverless tier, no infra to run.
C Weaviate — open-source vector DB, self-hosted on Kubernetes, full control over indexing.

---

DAY 28 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why D wins (Qdrant):
Qdrant is purpose-built for exactly this workload. Rust core = low latency and predictable memory
under load. At 300 req/s you need an index that handles concurrent ANN queries without degrading
— Qdrant's HNSW implementation is tuned for this.
The killer feature here is payload filtering. In a B2B product, users search within a workspace,
tenant, or product line — not globally. Qdrant handles vector search + metadata filter in one pass.
Every other option forces post-filtering, which blows up recall and adds round-trips.
Self-hosted gives you full control over HNSW params (m, ef_construction), memory mapping, and on-
disk indexing — critical when your corpus grows past RAM.
