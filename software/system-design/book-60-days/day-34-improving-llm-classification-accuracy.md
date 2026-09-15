---
id: software/system-design/book-60-days/day-34-improving-llm-classification-accuracy
canonical_question: Improving LLM Classification Accuracy
aliases:
- System Design Day 34
- Improving LLM Classification Accuracy
- Day 34 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 34: Improving LLM Classification Accuracy

DAY 34 · SYSTEM DESIGN
Improving LLM Classification Accuracy
Your AI feature works in the demo.
It fails in production 3 weeks later. Nobody touched the model. Nobody changed the code.
The only thing that changed: the inputs got messier.
Here's the setup:
You're at a SaaS company. 50,000 support tickets a week. Your team builds an AI triage system — GPT-4o
classifies each ticket into 6 categories (billing, bug, feature request, account access, security, other) so the
right team gets it instantly.
In dev, it nails 71% accuracy. You need 90%+ to cut manual review.
The model is locked. The budget for inference isn't unlimited. You need to close the 19-point gap.
Here are your four options:
A) Zero-shot with a better system prompt — rewrite the instructions, add explicit category definitions,
specify edge case rules. No examples.
B) Few-shot examples — add 3–5 real classified tickets directly in the prompt. One example per category
edge case.

---

DAY 34 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
B — Few-shot Best answer here
Accuracy: 88–93%. Cost increase: near-zero.
Few-shot shifts the model from reading rules to pattern-matching against real examples. Fundamentally
stronger signal.
The part most teams get wrong: they pick the obvious examples. A crystal-clear billing ticket. A
textbook bug report. Those teach the model nothing it didn't already know.
You want the ambiguous ones. The ticket that looks like billing but is account access. The feature
request that reads like a bug. Those are where the model currently fails — and those are the examples
that close the gap.
Get the selection right, you close most of the 19 points without touching anything else.
Answer 2
A — Zero-shot with a better system prompt
Accuracy ceiling: ~78–82%.
This is where every team starts. You iterate the prompt, add category definitions, enumerate edge
cases. It feels like progress. And for a while it is.
The hard wall: instructions describe categories. They can't show the model where the ambiguous cases
land.
Real example: you define "billing" as anything about charges or invoices. Then you get this ticket — "I
can't log in and I was charged twice last month." Billing? Account access? Both?
No amount of rewriting tells the model which bucket that gets. It guesses wrong 20–25% of the time
on edge cases. And your dataset is full of edge cases. The ceiling is real.
