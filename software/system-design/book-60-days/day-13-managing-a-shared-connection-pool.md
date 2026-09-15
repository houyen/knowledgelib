---
id: software/system-design/book-60-days/day-13-managing-a-shared-connection-pool
canonical_question: Managing a Shared Connection Pool
aliases:
- System Design Day 13
- Managing a Shared Connection Pool
- Day 13 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 13: Managing a Shared Connection Pool

DAY 13 · SYSTEM DESIGN
Managing a Shared Connection Pool
You're running 3 workloads against the same Postgres RDS instance. max_connections = 300. They all need
a connection pool. None of them want to share.
Here's the setup:
→  NestJS REST API on ECS Fargate. Short transactions, 800 RPS, 10 tasks × 40 pool = 400 connections
requested.
→  Background job workers. Long-running analytics queries. Hold a connection for 30–90 seconds each.
→  Lambda functions. Bursty, cold-start heavy, 0–200 concurrent invocations.
Three clients. One database. 300 max connections. Math doesn't math.
You need to pool without breaking any of them. Pick your poison:
A PgBouncer transaction mode for everyone: single pooler in front of RDS, maximum
multiplexing.
B PgBouncer session mode for the workers + transaction mode for the REST API: split pooler
config by workload type. Lambda goes through one of them.

---

DAY 13 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: B — PgBouncer session mode for workers + transaction mode for REST API ✅
This one separates engineers who've actually run PgBouncer in prod from ones who've only read the
docs. Here's the breakdown:
Why B wins (split pooler config by workload type):
The whole point of PgBouncer is multiplexing — one backend Postgres connection serves many client
connections, but only when it's safe to hand the connection back between transactions. That's
transaction mode.
Transaction mode is perfect for the NestJS REST API: short transactions, 800 RPS, no session state, no
SET LOCAL, no advisory locks held across queries, no prepared statements that need to survive. The
REST API's 400 requested client connections collapse down to ~30–50 actual backend connections to
Postgres. Math suddenly maths.
Transaction mode is catastrophic for the analytics workers. Their queries run 30–90 seconds and span
multiple transactions — some hold session state, some use temp tables, some use SET search_path,
some use cursors. Hand the connection back between transactions and that state is gone. Worse: at
800 RPS from the API side, the worker's chance of getting the same backend connection back on the
next transaction is basically zero. The worker silently breaks.
