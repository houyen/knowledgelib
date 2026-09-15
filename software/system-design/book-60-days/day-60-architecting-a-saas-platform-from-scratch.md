---
id: software/system-design/book-60-days/day-60-architecting-a-saas-platform-from-scratch
canonical_question: Architecting a SaaS Platform from Scratch
aliases:
- System Design Day 60
- Architecting a SaaS Platform from Scratch
- Day 60 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 60: Architecting a SaaS Platform from Scratch

DAY 60 · SYSTEM DESIGN
Architecting a SaaS Platform from Scratch
You're designing the architecture for a new SaaS platform from scratch.
It needs to handle 50,000 requests per second at launch. Multi-tenant. Real-time data. Global users. AI
inference built in.
Your CTO gives you 3 months and a blank slate.
You've been thinking about this for a week. You finally sit down to draw the first box.
Here's what engineers actually debate in that room:
A) Start with a distributed microservices architecture — services for auth, billing, inference, and core
domain from day one. Scale each independently.
B) Start with a modular monolith — one deployable unit with clean internal module boundaries. Extract
services only when a specific boundary proves it needs it.
C) Start with serverless — Lambda/Cloud Functions for every endpoint, DynamoDB for state, SQS for
async. Zero infra to manage, scales to zero between bursts.
D) Start with an event-driven architecture — Kafka as the backbone, all services communicate through
events, no direct API calls between services from day one.

---

DAY 60 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
B) Modular Monolith — right
The constraint isn't scale. It's the 3-month runway plus uncertainty about domain boundaries.
A modular monolith gives you:
• Fast iteration — no network serialization overhead, no cross-service API contracts to version
• Real module boundaries enforced in code (auth, billing, inference, core domain — no shared DB
tables, no cross-module direct calls)
• Single deploy, single observability surface, single transaction boundary
• The option to extract services later — when you know exactly which boundary is real
When billing hits 10k RPS independently and needs separate scaling, you extract it. The boundary is
already clean. The migration is a refactor, not a rewrite.
