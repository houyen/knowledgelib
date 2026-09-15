---
id: software/system-design/book-60-days/day-42-designing-memory-for-an-ai-agent
canonical_question: Designing Memory for an AI Agent
aliases:
- System Design Day 42
- Designing Memory for an AI Agent
- Day 42 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 42: Designing Memory for an AI Agent

DAY 42 · SYSTEM DESIGN
Designing Memory for an AI Agent
Your AI agent remembered the user's name.
Then it forgot what it was doing.
Here's the setup:
User asks the agent: book the cheapest flight to NYC, search hotels under $150/night, then compare total
trip cost.
By step 3, the agent calls the LLM with 8,000 tokens of raw conversation history — and still answers as if
it's turn 1.
You need a memory architecture before this ships. Which one do you pick?
A) In-context window only — full conversation stays in the system prompt. Simple. Breaks at ~15 turns or
8K tokens, whichever comes first.
B) Vector memory store — embed past turns, retrieve the top-k by semantic similarity at query time. Works
great until "NYC flight" pulls a memory about a past NYC trip instead of the current task.
C) Episodic memory with summarization — compress old turns into structured event summaries, inject the
relevant ones per request. More complex to build. Much harder to confuse.

---

DAY 42 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
C — Episodic memory with summarization
Right answer for task-oriented agents. The pattern:
→  Keep the last N turns in context (short-term)
→  Compress older turns into structured event summaries (episodic)
→  Inject only relevant summaries per new request
It's how production agents at Anthropic, LangChain Memory v2, and OpenAI Assistants API all
converge. More engineering upfront — but the only pattern that degrades gracefully at scale.
