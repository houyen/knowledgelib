---
id: software/system-design/book-60-days/day-58-observability-for-llm-agent-pipelines
canonical_question: Observability for LLM Agent Pipelines
aliases:
- System Design Day 58
- Observability for LLM Agent Pipelines
- Day 58 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 58: Observability for LLM Agent Pipelines

DAY 58 · SYSTEM DESIGN
Observability for LLM Agent Pipelines
It's 2am. Your LLM agent is on fire and every log says HTTP 200.
You shipped an AI-powered support agent 6 weeks ago. It calls tools, chains 4-5 prompts per request, hits
vector search, calls back into your API. Users are complaining. Answers are wrong. Token bills are 3x what
they were last week.
You open your logs. Everything is green. You open your traces. You see one span called POST /chat that
took 14 seconds. That's it. That's your entire visibility.
Here's the setup:
NestJS API →  OpenAI (GPT-4o + GPT-4o-mini) + Anthropic (Claude Sonnet fallback)
~8,000 agent runs/day, each chains 3-7 LLM calls + 2-4 tool calls
Token spend jumped from $180/day to $540/day this week, no idea which flow caused it
Eval suite passes 94% in CI, prod users are hitting hallucinations you can't reproduce
On-call engineer literally cannot answer "why is this run slow / expensive / wrong?"
You have one sprint to fix the visibility problem before the next incident. What do you instrument first?

---

DAY 58 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins:
Every problem in the scenario is the same root cause — you can't see the shape of a single agent run.
Slow? →  Which of the 7 LLM calls was slow.
Expensive? →  Which model on which step burned the tokens.
Wrong? →  Which retrieval returned garbage that poisoned the next prompt.
None of those questions have answers without a trace. And LLM traces aren't HTTP traces — you need
span-level attributes: model name, prompt tokens, completion tokens, cost, tool name, retrieval doc
IDs, and the actual prompt/response payload. That's what LangSmith, Helicone, Arize, and Langfuse
give you out of the box.
Once you have it: the 14-second span opens into 7 sub-spans. You see the one that took 9s was a
Claude fallback triggered by a rate limit. The $540/day spike is one user hammering an agent that
recursively calls itself. The hallucinations correlate with retrievals that returned 0 chunks.
