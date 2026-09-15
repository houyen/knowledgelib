---
id: software/system-design/book-60-days/day-10-distributed-transactions-across-services
canonical_question: Distributed Transactions Across Services
aliases:
- System Design Day 10
- Distributed Transactions Across Services
- Day 10 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 10: Distributed Transactions Across Services

DAY 10 · SYSTEM DESIGN
Distributed Transactions Across Services
Order #4471 just hit your system at 14:02. The flow:
1. OrderService creates the order (Postgres) ✅
2. PaymentService charges $89.50 to Stripe ✅
3. InventoryService tries to reserve the SKU →  fails (oversold by 3 units)
4. ShippingService never gets called
You're now holding the customer's money, no inventory to ship, and an order stuck in PENDING. In a
monolith you'd wrap all 4 in a transaction and ROLLBACK. You can't do that across 4 services with 4
databases.
What do you reach for?
A Choreography Saga — each service publishes events, the next reacts, failures trigger
compensating events backward through the chain.
B Orchestration Saga — a central orchestrator (a state machine) calls each service in order and
dispatches compensations on failure.

---

DAY 10 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
✅  Answer: B — Orchestration Saga
Why B wins:
4-step checkout with strict ordering + per-step compensations = exactly what an orchestrator is built
for. Stand up a CheckoutSaga state machine (Temporal, AWS Step Functions, Camunda, or hand-
rolled). It calls each service in order: OrderService →  PaymentService →  InventoryService →
ShippingService. Each step has a registered compensation: CancelOrder, RefundPayment,
ReleaseInventory. When Inventory fails, the orchestrator walks backward and refunds automatically.
State is durable, observable, replayable. At 3am you open the orchestrator UI and see exactly which
step failed with full inputs/outputs.
