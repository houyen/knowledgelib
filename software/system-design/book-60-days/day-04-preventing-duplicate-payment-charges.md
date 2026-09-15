---
id: software/system-design/book-60-days/day-04-preventing-duplicate-payment-charges
canonical_question: Preventing Duplicate Payment Charges
aliases:
- System Design Day 04
- Preventing Duplicate Payment Charges
- Day 04 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 04: Preventing Duplicate Payment Charges

DAY 04 · SYSTEM DESIGN
Preventing Duplicate Payment Charges
A user taps "Pay $499" on checkout.
The spinner hangs. They tap it again. And once more.
Three requests hit your Payments API. Two of them actually succeed. The customer is charged $1,497 and
opens a support ticket before your on-call even sees the alert.
Here's the setup:
Mobile →  POST /payments { orderId: "ord_8821", amount: 499 }
Network stalls on the first request →  client retries twice
Your service receives 3 near-identical POSTs within 4 seconds
Stripe gets charged 3 times. Your DB writes 3 payment rows.
You have one sprint to make sure a retried request never double-charges again. What do you do?
A Add a unique constraint on (orderId, amount) in the payments table — the second insert fails,
problem solved.

---

DAY 04 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: B — Idempotency-Key header ✅
Here's why, and why the other three are the exact mistakes I've seen in real post-mortems:
Why B wins (Idempotency-Key):
The client generates a UUID before the first request and attaches it as Idempotency-Key: 7f3e... on
every retry of that same logical operation. Your server does the work once, stores {key →  response} in
a durable store (Postgres, DynamoDB, Redis with persistence — not plain Redis), and on any retry
with the same key, it returns the original response without re-executing the charge.
Critical detail most people miss: you cache the full response (status code + body), not just "I saw this
key." If retry #2 arrives while retry #1 is still processing, you make it wait or return a 409 — never let
two executions race with the same key.
This is exactly what Stripe (Idempotency-Key), PayPal (PayPal-Request-Id), Shopify, and AWS
(ClientRequestToken on half their APIs) all ship. It's the only approach that handles the full failure
matrix: network retries, client-triggered retries, load balancer retries, and "the request succeeded but
the response got lost" — which is the nastiest case and the one the other three options silently fail on.
