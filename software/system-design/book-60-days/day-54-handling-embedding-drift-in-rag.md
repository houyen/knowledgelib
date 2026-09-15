---
id: software/system-design/book-60-days/day-54-handling-embedding-drift-in-rag
canonical_question: Handling Embedding Drift in RAG
aliases:
- System Design Day 54
- Handling Embedding Drift in RAG
- Day 54 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 54: Handling Embedding Drift in RAG

DAY 54 · SYSTEM DESIGN
Handling Embedding Drift in RAG
You built a RAG pipeline. Works great in dev.
6 months later, your users complain: "The search results are garbage."
You haven't changed a line of code.
Here's what happened:
Your product evolved. New features, new docs, new support tickets. The data drifted — but your
embedding index didn't.
Now you're serving a 400GB FAISS index that was last rebuilt in January. Your chunks are stale. Your
nearest-neighbor results point to deprecated docs. Your LLM is confidently hallucinating from outdated
context.
You need to fix this. 4 engineers each propose a solution:
A) Scheduled full rebuild
Every Sunday, re-embed the entire corpus from scratch. Replace the index atomically. Slow (4h+ at scale),
expensive, but always fresh.
B) Incremental upserts + soft delete

---

DAY 54 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
C is the right answer — Embedding Version Registry + Hot Swap
This is the only solution that handles the real problem: your embedding model changed. When you
fine-tune or upgrade your model, Option A and B still serve a mixed index — some vectors from
model v1, some from v2. Your cosine similarity math breaks because you're comparing vectors from
different embedding spaces. They're not comparable. C is the only option that tracks which model
produced which vector and routes queries to the correct index version during migration. Two indexes in
parallel during transition = zero downtime, zero mixed-space comparisons.
The production win: you can migrate 10% of traffic to the new index, validate retrieval quality, then
cut over. No big bang. No 4-hour Sunday rebuild blocking your team.
