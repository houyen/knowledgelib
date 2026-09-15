---
id: software/system-design/book-60-days/day-11-handling-webhook-retries-idempotently
canonical_question: Handling Webhook Retries Idempotently
aliases:
- System Design Day 11
- Handling Webhook Retries Idempotently
- Day 11 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 11: Handling Webhook Retries Idempotently

DAY 11 · SYSTEM DESIGN
Handling Webhook Retries Idempotently
Stripe just sent your server a charge.succeeded webhook.
Your pod was mid-restart. The webhook timed out. Stripe will retry — but now you're racing.
Here's the setup:
NestJS API on ECS, 4 tasks behind an ALB. Stripe POSTs charge.succeeded events to /webhooks/stripe. You
have ~10s to return a 200 before Stripe times out and queues a retry. On Black Friday you're handling ~80
webhooks/sec.
Three failure modes are already happening in prod:
• Pod restarts mid-deploy →  webhook missed →  Stripe retries →  you process it, but a second pod also
processed the original →  double charge confirmation email sent
• DB is slow at peak →  handler takes 12s →  Stripe times out →  retries →  now you're processing the same
event twice while the first one is still running
• Stripe sends charge.succeeded then charge.refunded 200ms apart →  your queue delivers them out of
order →  you mark the order paid AFTER it was already refunded
The handler is a 30-line function that does the right thing 99% of the time. The 1% is killing you.

---

DAY 11 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: C — Verify signature, return 200 immediately, push to an internal queue ✅
Here's why, and why the other three trick smart engineers:
Why C wins (Sync receipt + async processing):
The fundamental problem is that Stripe's clock and your handler's clock are decoupled. Stripe gives
you ~10 seconds to ACK. Your DB write, your fraud check, your email send — none of that should
live inside that 10-second window. Ever.
The pattern: validate the HMAC signature in <5ms, write the raw payload to SQS / Kafka / Redis
Streams, return 200. Now your handler is bounded by network + signature verification, not by
whatever your downstream services are doing today. Pod restart mid-processing? The message is
already durable in the queue — a worker picks it up. DB slow? The webhook endpoint doesn't care —
it returned 200 in 8ms. This is what Stripe, Shopify, and GitHub literally tell you to do in their own
webhook docs.
