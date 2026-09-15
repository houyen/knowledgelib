---
id: software/system-design/book-60-days/day-01-decoupling-mobile-from-backend-services
canonical_question: Decoupling Mobile from Backend Services
aliases:
- System Design Day 01
- Decoupling Mobile from Backend Services
- Day 01 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 01: Decoupling Mobile from Backend Services

Contents

---

DAY 01 · SYSTEM DESIGN
Decoupling Mobile from Backend Services
our mobile app talks to 3 backend services directly.
A 4th one ships next sprint. The mobile team is already drowning.
Every new service means a new domain to whitelist, a new auth scheme to wire, and a new error shape to
parse. You're asked to reduce coupling before NotificationService lands.
Here's the setup:
Mobile →  UserService (users.api.com)
Mobile →  OrderService (orders.api.com)
Mobile →  PaymentService (payments.api.com)
…and NotificationService next sprint.
The client is doing routing the backend should be doing. What do you do?
A Add an API Gateway — single entry point, all services hide behind one domain.
B Build a BFF (Backend for Frontend) — a dedicated aggregation layer tailored for mobile.

---

DAY 01 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins (API Gateway):
One domain. One auth flow. One error contract. The client stops caring that UserService,
OrderService, and PaymentService live on different hosts — the gateway hides them behind
api.yourapp.com/users, /orders, /payments. When NotificationService ships next sprint, you add one
route. The mobile app ships zero changes. That's what "future-proof" actually means at the transport
layer: new services cost nothing on the client side.
It also centralizes the things you don't want scattered across 4 codebases: authN/authZ, rate limiting,
request logging, TLS termination, versioning. Netflix, Stripe, and every mature fintech run some form
of this.
