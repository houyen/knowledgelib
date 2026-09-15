---
id: software/system-design/book-60-days/day-29-coordinating-a-multi-agent-workflow
canonical_question: Coordinating a Multi-Agent Workflow
aliases:
- System Design Day 29
- Coordinating a Multi-Agent Workflow
- Day 29 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 29: Coordinating a Multi-Agent Workflow

DAY 29 · SYSTEM DESIGN
Coordinating a Multi-Agent Workflow
You have an AI product with 4 specialized agents: a Planner, a Researcher, a Coder, and a Reviewer.
The Planner breaks down the task. The Researcher pulls context. The Coder implements. The Reviewer
catches bugs.
Simple on paper. In production, it's falling apart.
Here's what's happening:
• The Researcher sometimes returns before the Planner finishes →  Coder gets incomplete context
• The Reviewer flags issues →  but there's no retry loop, so bugs ship anyway
• One agent timeout hangs the entire pipeline for 40 seconds
• You have no visibility into which agent failed or why
You need to redesign the orchestration layer. What do you do?
A) Centralized orchestrator — one controller calls each agent in sequence, owns retry logic, tracks state in
a DB, times out per step individually.
B) Choreography via event bus — agents publish/subscribe to events, no central controller, each agent
triggers the next autonomously.

---

DAY 29 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Correct Answer: C — DAG-based execution
Your pipeline has hard dependencies (Coder must wait for BOTH Planner AND Researcher) AND
needs retry loops (Reviewer →  Coder on failure).
A DAG models this explicitly:
Planner ──┐
├──► Coder ──► Reviewer
Researcher┘              │
◄───────── (retry on failure)
What this solves directly:
• Race condition →  DAG blocks Coder until both upstream nodes complete. No manual checks.
• Timeout hanging pipeline →  each node has its own deadline. One agent timeout doesn't freeze
everything.
• No retry loop →  retry is a first-class edge in the graph, not bolted-on logic.
• No visibility →  DAG engines give you a full execution trace per run.
