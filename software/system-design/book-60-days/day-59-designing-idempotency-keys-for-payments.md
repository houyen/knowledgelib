---
id: software/system-design/book-60-days/day-59-designing-idempotency-keys-for-payments
canonical_question: Designing Idempotency Keys for Payments
aliases:
- System Design Day 59
- Designing Idempotency Keys for Payments
- Day 59 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 59: Designing Idempotency Keys for Payments

DAY 59 · SYSTEM DESIGN
Designing Idempotency Keys for Payments
Your payment service charged a customer twice.
Same request. Different response code. Client retried. You had no dedup logic.
That's not a race condition. That's a missing design decision.
And the decision isn't whether to use idempotency keys. It's how you generate them.
Here's the scenario:
Your API processes payments. Clients can and will retry on network failures. Your downstream calls (Stripe,
Kafka, wallet credit) cannot be undone once triggered. A 500 or timeout on your side looks identical to a
"try again" from the client's perspective.
Which idempotency strategy do you go with?
A) Client-generated keys
Client sends a UUID with every request (Idempotency-Key: ). Your server stores key →  response in Redis
with a 24h TTL. Duplicate request? Return cached response. No reprocessing.
B) Server-generated keys

---

DAY 59 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
A) Client-generated keys — ✅  GOLD STANDARD FOR EXTERNAL APIs
This is how Stripe does it. How Braintree does it. Reason: the client owns the intent, so the client
owns the key.
The flow that actually works in production:
1. Write the key with status pending before processing (Redis SET NX)
2. Process the payment
3. Update key to completed with the full response body
Write the key first. Not after. If you crash between the payment succeeding and the key write —
you've charged the card with no dedup record. Next retry charges again.
Key scoping matters: scope to (customer_id, key) not globally. TTL: 24h standard, 72h for aggressive
retry clients. After expiry, same UUID = new request — document this.
