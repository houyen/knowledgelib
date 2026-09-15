---
id: software/system-design/book-60-days/day-55-parallel-agents-with-shared-state
canonical_question: Parallel Agents with Shared State
aliases:
- System Design Day 55
- Parallel Agents with Shared State
- Day 55 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 55: Parallel Agents with Shared State

DAY 55 · SYSTEM DESIGN
Parallel Agents with Shared State
You built an agent. It works.
Now you need 5 of them running in parallel, sharing state, and handing off work to each other.
Your pipeline breaks on the first real workload.
Here's the setup:
You're building a research agent system. A user asks a complex question. You need to:
• Fan out to 3 specialized sub-agents simultaneously
• One agent might spawn 2 more based on what it finds
• They all write back to shared context
• A final agent synthesizes everything
Classic multi-agent orchestration. You have 4 options for how agents coordinate.
A) Centralized Orchestrator — one controller agent dispatches tasks, collects results, manages shared
state. Agents are dumb workers.

---

DAY 55 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: A — Centralized Orchestrator
Here's the full breakdown — and where each pattern actually belongs:
Why A wins (Centralized Orchestrator):
One agent owns the plan. It dispatches, collects, retries, and synthesizes. Every sub-agent is stateless
and dumb on purpose — they receive a task, return a result, done.
This isn't a limitation. It's a feature.
When something fails, you know exactly where to look: the orchestrator. It holds the retry logic, the
timeout budgets, the fallback paths. Sub-agents can die and restart without corrupting global state
because the orchestrator is the only one maintaining it.
LangGraph, CrewAI, and every production-grade agentic framework defaults to this model for a
reason. It's debuggable, observable, and deterministic. You can replay an orchestrator run from its
state log. Try doing that with peer-to-peer handoffs.
