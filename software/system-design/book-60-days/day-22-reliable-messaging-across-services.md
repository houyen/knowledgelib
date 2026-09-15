---
id: software/system-design/book-60-days/day-22-reliable-messaging-across-services
canonical_question: Reliable Messaging Across Services
aliases:
- System Design Day 22
- Reliable Messaging Across Services
- Day 22 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 22: Reliable Messaging Across Services

DAY 22 · SYSTEM DESIGN
Reliable Messaging Across Services
Your payment service just charged a customer.
It writes to the DB. Now it needs to tell the notification service: "Send the confirmation email."
The HTTP call times out. Did it arrive? You don't know. You retry. Customer gets two emails.
You've just hit the Two Generals Problem. It's not a bug. It's a proof.
No protocol over an unreliable channel can guarantee both sides agree on the final message. Not HTTP. Not
TCP. Not your retry loop. The uncertainty is mathematically irreducible.
Here's the setup:
PaymentService (Node.js, PostgreSQL) →  NotificationService (Go)
~40ms p99 latency, occasional 504s under load.
You need to send exactly one confirmation email per payment — no double-sends, no missed sends.
What do you build?
A) Retry with exponential backoff until NotificationService returns 200. If you keep retrying until you get
an ACK, you know it arrived.

---

DAY 22 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
D — SQS + at-least-once + idempotency key (CORRECT)
The only answer that accepts the impossibility and designs around it. At-least-once means the message
will arrive — maybe twice. Idempotency on the consumer side (payment_id:email:v1 in a dedup
table) makes the second delivery a no-op. No missed sends, no double-sends in practice. This is
exactly how Stripe and AWS handle it. The queue absorbs the uncertainty. Idempotency absorbs the
duplicates.
Answer 2
A — Retry until ACK (SENIOR ENGINEER TRAP)
Feels airtight. It's not. What if the 200 response is what timed out — not the request?
NotificationService sent the email AND returned 200, but you never saw the response. So you retry.
Second email sent. Now you need to confirm your ACK arrived too... which is the Two Generals
recursion. No finite number of retries closes this loop. More handshakes = more latency and more
failure surfaces, not more certainty.
