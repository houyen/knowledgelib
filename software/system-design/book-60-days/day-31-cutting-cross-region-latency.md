---
id: software/system-design/book-60-days/day-31-cutting-cross-region-latency
canonical_question: Cutting Cross-Region Latency
aliases:
- System Design Day 31
- Cutting Cross-Region Latency
- Day 31 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 31: Cutting Cross-Region Latency

DAY 31 · SYSTEM DESIGN
Cutting Cross-Region Latency
Your e-commerce platform just crossed 2M daily active users. 70% are in the US, 30% in Europe.
Latency complaints are piling up from European users — 380ms average round-trip to your US-East region.
Support tickets are up 40%. Black Friday is in 6 weeks.
Your infrastructure: single AWS us-east-1 region, RDS PostgreSQL (primary), Redis cache, 12 microservices
behind an API Gateway.
You need to get European latency under 80ms. The engineering team is debating four approaches.
Here's your constraint: you cannot afford a full database rewrite, and you need this shipped before Black
Friday.
A) Active-Active multi-region — deploy the full stack in eu-west-1, use a distributed database
(CockroachDB or Aurora Global), route users to the nearest region. Writes go to both regions
simultaneously.
B) Active-Passive with read replicas — keep us-east-1 as primary, spin up eu-west-1 as a hot standby with
read replicas. European reads go local, writes still go to US. Failover in minutes if US goes down.
C) CDN + Edge caching — keep the single region, push static assets and cacheable API responses to
CloudFront edge nodes in Europe. No database changes.

---

DAY 31 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins:
The constraint is the answer. You can't rewrite the database, and you have 6 weeks.
European users are complaining about read latency — browsing products, checking order status,
loading their profile. Those are reads. An RDS read replica in eu-west-1 costs you 1–2 days of infra
work and immediately moves European reads to ~15ms instead of 380ms. Writes still go to us-east-1
(acceptable — users tolerate slightly higher write latency for checkout). Replication lag is typically
under 100ms.
Active-passive also gives you a real failover story: US goes down →  promote EU replica in minutes.
