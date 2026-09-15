---
id: software/system-design/book-60-days/day-48-how-an-agent-chooses-which-tools-to-call
canonical_question: How an Agent Chooses Which Tools to Call
aliases:
- System Design Day 48
- How an Agent Chooses Which Tools to Call
- Day 48 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 48: How an Agent Chooses Which Tools to Call

DAY 48 · SYSTEM DESIGN
How an Agent Chooses Which Tools to Call
Your AI agent just got a user message: "Book me a flight to Dubai next Friday."
The LLM has access to 12 tools: search_flights, get_user_preferences, check_calendar, book_flight,
send_confirmation, get_weather…
How does the agent decide which tools to call, in what order, and when to stop?
A) ReAct loop — model reasons step-by-step, emits a "thought" then picks one tool at a time, observes
output, repeats until it self-decides it's done
B) Parallel tool calling — model emits ALL required tool calls in a single response, executes them
concurrently, feeds all results back in one context update
C) Forced function schema — you lock the model into a strict JSON schema per turn; it can't produce free
text, only structured tool calls you defined
D) Planner-executor split — a lightweight planner LLM creates a tool call DAG upfront, a separate
executor runs the graph, results flow back to planner only at checkpoints

---

DAY 48 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
A — ReAct loop Correct for most cases
ReAct (Reason + Act) is the dominant production pattern for a reason.
The model emits a "Thought:" explaining what it's doing, then an "Action:" with a single tool call, then
observes the result before deciding what's next.
Why it works:
• Each step is observable and debuggable
• The model can bail out, retry, or change direction after each tool result
• Works even with tools that have side effects — you can gate dangerous calls
• Supported natively by OpenAI, Anthropic, LangChain, LlamaIndex out of the box
The trap: ReAct is sequential. If you need get_user_preferences AND check_calendar AND
search_flights all before book_flight, you're making 3 round trips when you could make 1.
