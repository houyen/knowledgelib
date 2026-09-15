---
id: software/system-design/book-60-days/day-27-keeping-an-llms-answers-up-to-date
canonical_question: Keeping an LLMs Answers Up to Date
aliases:
- System Design Day 27
- Keeping an LLMs Answers Up to Date
- Day 27 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 27: Keeping an LLMs Answers Up to Date

DAY 27 · SYSTEM DESIGN
Keeping an LLM’s Answers Up to Date
Your LLM answers are wrong. Not hallucination-wrong — outdated-wrong.
You shipped a customer support bot on GPT-4. It's trained through early 2024. Your product changed 14
times since then. Every week, users get answers that were accurate 8 months ago and are flat-out wrong
today.
The team is debating the fix.
Here's the setup:
NestJS API →  OpenAI GPT-4 + PostgreSQL (product knowledge base)
~2,000 support queries/day, 15% return wrong answers tied to stale knowledge
Knowledge base updates weekly — new pricing, new features, deprecated flows
Budget: mid-size startup, not training custom models from scratch
You need accurate, up-to-date answers without re-training on every product update
What do you do?
A) RAG — embed your knowledge base, retrieve relevant chunks at query time, inject into context. Model
stays the same, knowledge is always fresh.

---

DAY 27 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: A — RAG
The problem is freshness — the model doesn't know what changed, not that it doesn't understand
your domain.
RAG separates knowledge from reasoning. The model stays frozen (no retraining cost, no deployment
cycle). Your knowledge base lives in a vector store — update a doc, re-embed it, done. New pricing
ships Monday, your bot knows it by Monday.
At runtime: user asks →  embed query →  retrieve top-K relevant chunks →  inject into context →
model reasons over fresh, accurate content.
You've turned a model problem into a data pipeline problem. Every engineering team already knows
how to solve data pipelines.
