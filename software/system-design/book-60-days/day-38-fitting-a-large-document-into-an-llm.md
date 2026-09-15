---
id: software/system-design/book-60-days/day-38-fitting-a-large-document-into-an-llm
canonical_question: Fitting a Large Document into an LLM
aliases:
- System Design Day 38
- Fitting a Large Document into an LLM
- Day 38 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 38: Fitting a Large Document into an LLM

DAY 38 · SYSTEM DESIGN
Fitting a Large Document into an LLM
Your LLM has 128K tokens.
Your document has 150K words.
Something has to give. What do you do?
A Chunk the document into fixed-size pieces and embed each one — retrieve the top-k at query
time.
B Use a sliding window — process the document in overlapping chunks, stitch the outputs together.
C Summarize each section progressively — feed the running summary forward as context.
D Truncate to the most recent tokens and hope the answer is near the end.

---

DAY 38 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins (RAG with chunked embeddings):
You split the document into overlapping chunks (~500 tokens, ~10–20% overlap), embed each one,
store in a vector DB (Pinecone, pgvector, Qdrant), and retrieve top-k at query time.
This scales to any document size. Your LLM context at inference only sees the retrieved chunks —
staying well inside the context window. Latency stays low because retrieval is a fast ANN lookup, not a
sequential scan.
The catch: chunking boundaries destroy semantic coherence. If a clause starts on page 12 and
resolves on page 13, a hard chunk boundary between them means neither chunk retrieves well for
that question. This is why overlap and chunk size tuning matter so much. Most teams underestimate
this.
Production fix: chunk at sentence or paragraph boundaries, not character counts. Hybrid retrieval
(keyword + semantic) handles the edge cases.
