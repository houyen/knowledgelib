---
id: software/system-design/book-60-days/day-07-event-ordering-in-a-message-queue
canonical_question: Event Ordering in a Message Queue
aliases:
- System Design Day 07
- Event Ordering in a Message Queue
- Day 07 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 07: Event Ordering in a Message Queue

DAY 07 · SYSTEM DESIGN
Event Ordering in a Message Queue
Your order service publishes 3 events per order: created, paid, cancelled.
Standard SQS queue, 5 consumers, ~2K orders/minute at peak.
Last night, prod alerted: 47 orders stuck in "cancelled" state with no "created" record. Customers got
refunded for orders that were never marked as placed. Finance is not happy.
You dig in. The order was placed, paid, and cancelled within 400ms. Three messages hit SQS in order.
Three consumers picked them up in parallel. "cancelled" got processed first. State machine rejected
"created" as invalid. Data is now wrong.
Here's the setup:
OrderService →  SQS (standard) →  5 workers →  Postgres
Events: order.created →  order.paid →  order.cancelled
Problem: workers process in parallel, SQS standard doesn't guarantee order, downstream state machine
breaks when events arrive out of sequence.
You have until Monday. What do you do?

---

DAY 07 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
✅  Answer: A — SQS FIFO + MessageGroupId per order_id
Why A wins:
You don't need global ordering — you need per-order ordering. Set MessageGroupId = order_id. FIFO
guarantees messages with the same group ID are delivered in exact send order, with only one
consumer processing that group at a time. Your 2K orders/min still fan out across 5 workers —
throughput is unchanged. Order #12345's created →  paid →  cancelled always lands in sequence.
Cost: a few ms latency. Ship it Monday.
Answer 2
Why B is the trap (reorder buffer):
Fools senior engineers on the whiteboard. You'd end up building: in-memory buffer per order_id +
TTL logic + dead-letter path for gaps + crash recovery + stuck buffer monitoring. You just rebuilt
FIFO in app code. With more bugs. And you own every edge case. B is valid only when you can't use
FIFO (e.g. Kafka with a taken partition key). That's not this situation.
Answer 3
Why C is wrong (Saga):
Saga is for long-running distributed transactions with compensating actions (book flight →  charge
card →  reserve hotel). Your problem is a state stream for one entity — not a multi-service transaction.
Forcing it into a Saga turns async events into sync RPC, increases coupling, and still doesn't fix
ordering.
