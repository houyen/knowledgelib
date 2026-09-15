---
id: software/system-design/book-60-days/day-51-isolating-noisy-tenants-in-multi-tenant-saas
canonical_question: Isolating Noisy Tenants in Multi-Tenant SaaS
aliases:
- System Design Day 51
- Isolating Noisy Tenants in Multi-Tenant SaaS
- Day 51 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 51: Isolating Noisy Tenants in Multi-Tenant SaaS

DAY 51 · SYSTEM DESIGN
Isolating Noisy Tenants in Multi-Tenant SaaS
You're building a B2B SaaS product. 50 enterprise customers. Each one wants their data isolated. Some are
on free plans. A few are paying $50k/year and demanding SLA guarantees.
Your current setup:
→  One database. One schema. A tenant_id column on every table.
→  One app server handling all traffic.
→  A free-tier customer running a badly-written bulk export just hammered your DB for 40 seconds. A
paying enterprise customer's checkout flow timed out.
Your investors are not happy. Neither is that enterprise customer.
The engineering question: how do you isolate tenants without rebuilding the whole product?
A) Keep one shared DB — add row-level security + query budgets per tenant to enforce limits.
B) Schema-per-tenant — every customer gets their own schema in the same Postgres instance, migrations
run per-schema.
C) Database-per-tenant (silo model) — each enterprise customer gets a dedicated DB. Free tier stays
pooled.

---

DAY 51 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why D wins (Middleware bridge — hybrid model):
This is the pattern Salesforce, HubSpot, and every mature B2B SaaS converges on eventually.
The architecture:
→  Free/small tenants →  shared pool DB (cost-efficient, acceptable risk)
→  Mid-tier tenants →  schema-per-tenant in a shared Postgres cluster
→  Enterprise tenants →  dedicated DB cluster (full isolation, SLA-able)
A tenant registry (Redis or a lightweight service) maps tenant_id →  connection config at request time.
Your app server doesn't care which model a tenant uses — it asks the registry and gets a connection
string back.
The payoff:
→  Noisy neighbor is contained. A runaway free-tier export can only hurt other free-tier tenants.
→  Enterprise customers can't touch each other. Period.
