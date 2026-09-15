---
id: software/system-design/book-60-days/day-21-choosing-a-real-time-streaming-transport
canonical_question: Choosing a Real-Time Streaming Transport
aliases:
- System Design Day 21
- Choosing a Real-Time Streaming Transport
- Day 21 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 21: Choosing a Real-Time Streaming Transport

DAY 21 · SYSTEM DESIGN
Choosing a Real-Time Streaming Transport
You're shipping an AI chat product. The LLM streams ~40 tokens/sec per user.
50,000 concurrent users on launch day. Browser clients only. Tokens flow one way: server →  user.
Your team meets to pick the transport. Everyone shows up with a strong opinion.
Here's the setup:
• Frontend: React in the browser
• Backend: Python (FastAPI) behind an ALB
• Payload: UTF-8 text tokens, ~5–20 bytes each
• Direction: server pushes, client just renders
• Reconnects must be invisible (mobile networks drop constantly)
The team lead says "WebSockets, obviously." The platform engineer pushes back. What do you ship?
A WebSockets — the default for "real-time," full-duplex, every chat app uses it.

---

DAY 21 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins (SSE):
The traffic is one-way. Server pushes tokens, client renders. That's it. The client never sends a token
back mid-stream — user input goes through a separate POST. So you're paying for full-duplex on a
half-duplex problem.
SSE is built for exactly this shape. One long-lived HTTP connection, text/event-stream, server writes,
browser's native EventSource reads. No protocol upgrade. No new framing. No new auth path.
The killer feature: automatic reconnect with Last-Event-ID. Browser drops, mobile switches from
WiFi to LTE — EventSource reconnects on its own and tells the server the last event it saw. You replay
from there. With WebSockets, you write that logic yourself, and you write it wrong the first three
times.
OpenAI's streaming API? SSE. Anthropic's streaming API? SSE.
