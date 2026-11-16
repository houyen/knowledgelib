---
id: software/system-design/book-60-days/resilience-and-traffic-control
canonical_question: How do you design distributed systems to withstand cascading failures, unbounded traffic spikes, and noisy neighbors?
aliases:
- handling backpressure and traffic spikes
- isolating noisy tenants in multi-tenant databases
- circuit breaker and bulkhead pattern comparison
- rate limiting algorithms token bucket vs fixed window
- safe deployment strategies for payment systems
- kafka consumer lag and load shedding patterns
- queue backpressure mitigation strategies
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 03, 14, 17, 20, 25, 51 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Resilience Patterns: Fault Isolation, Traffic Shaping, and Safe Delivery

## TL;DR
Resilience requires controlling entry rates and segmenting blast radiuses rather than endlessly adding downstream capacity. When services fail or traffic surges, throttle upstream producers, isolate execution pools with bulkheads, and cut off failed calls with circuit breakers. Decouple deployments from releases using targeted feature flags, and isolate noisy tenants through hybrid tiered infrastructure rather than naive per-tenant sprawl.

---

## Rate Limiting: Mitigating Boundary Bursts

### The Problem
A fixed cap of 100 requests per minute allows clients to send 90 requests at the end of a minute window and 90 requests at the beginning of the next, yielding 180 requests in four seconds and overwhelming downstream storage.

### Recommended Solution: Token Bucket
A token bucket algorithm maintains a bucket filled with up to 100 tokens that replenishes continuously at a fixed rate (e.g., ~1.66 tokens per second). Every incoming request consumes a token; empty buckets return HTTP 429 immediately.

Because replenishing is continuous rather than tied to wall-clock minute boundaries, a burst at the end of a minute drains the bucket, preventing a second burst immediately afterward. The algorithm requires $O(1)$ memory per client key, executes in $O(1)$ time, and provides smooth traffic shaping without boundary reset vulnerabilities.

### Tempting Alternatives and Why They Fail
- **Fixed Window Counter:** Resets its counter on the calendar minute, allowing double the allowed quota across window boundaries.
- **Sliding Window Log:** Tracks raw timestamps for every request to calculate rolling counts. While mathematically exact, storing every interaction creates severe memory bloat and latency spikes at high traffic volumes (e.g., 100,000+ keys).
- **Leaky Bucket:** Enforces a rigid outbound dispatch rate by queueing surplus requests. For customer-facing APIs, queueing introduces unwanted latency; immediately rejecting excess traffic via token bucket is preferable to holding requests.

| Algorithm | Boundary Safe? | Memory Cost | Latency Impact | Fits Public APIs? |
| :--- | :--- | :--- | :--- | :--- |
| **Fixed Window** | No (2x burst) | $O(1)$ per key | None | No |
| **Sliding Window Log** | Yes | $O(N)$ requests | High on reads | No |
| **Token Bucket** | Yes | $O(1)$ per key | None (fails fast) | **Yes** |
| **Leaky Bucket** | Yes | $O(N)$ queued | Adds queue lag | No (better for workers) |

---

## Fault Containment: Surviving Slow External Dependencies

### The Problem
An external fraud evaluation service deteriorates from a 200 ms response time to a 30-second hang, exhausting a service pod's 50-connection pool and knocking out independent routes like `/cart` and `/health`.

### Recommended Solution: Circuit Breaker Combined with Bulkheads
Combine a circuit breaker with a dedicated bulkhead pool. 

- The **bulkhead** allocates a dedicated slice of connections (e.g., 10 of 50) solely to the third-party dependency. The remaining 40 connections stay open for `/cart` and `/health`.
- The **circuit breaker** monitors failure counts or timeout rates. Once a threshold is breached, it trips to OPEN, instantly aborting calls with a fallback without holding a connection. After a cooldown, it allows a single probe request in HALF-OPEN state before deciding whether to resume normal operations.

### Tempting Alternatives and Why They Fail
- **Lower Timeouts with Retries:** Truncating timeouts to 2 seconds and adding retries amplifies outbound calls against a struggling service, transforming partial degradation into a complete outage via retry storms.
- **Circuit Breaker Alone:** Before the breaker hits its trip threshold, slow requests still hold connections from the shared pool, exhausting available slots and starving healthy endpoints before detection occurs.
- **Bulkhead Alone:** Isolates connection exhaustion from sibling routes, but every call routed to the external dependency still hangs for 30 seconds, degrading the primary checkout journey.

| Pattern Strategy | Sibling Endpoints Protected? | Slow Dependency Failed Fast? | Prevents Thundering Herd? |
| :--- | :--- | :--- | :--- |
| **Timeout + Retries** | No (accelerates pool drain) | No | No (creates retry storms) |
| **Breaker Alone** | No (leaks during detection) | Yes (after trip) | Yes (via half-open probe) |
| **Bulkhead Alone** | Yes | No (hangs until timeout) | No |
| **Breaker + Bulkhead** | **Yes** | **Yes** | **Yes** |

---

## Stream Backpressure: Handling Lag in Decoupled Consumers

### The Problem
A consumer processes 800 events per second through an external HTTP and database write pipeline, but producer traffic surges to 5,000 events per second, threatening JVM memory exhaustion on a queue that strictly prohibits dropping data.

### Recommended Solution: Rate-Limited Consumption with Load Shedding to Secondary Topics
Enforce an ingestion ceiling on the consumer (e.g., 1,000 events/sec) to keep memory usage stable. When intake exceeds downstream capacity, route surplus messages directly to a durable secondary overflow topic (`events.overflow`). A separate off-peak worker group processes this overflow topic when traffic recedes, preserving SLA guarantees without exhausting application memory.

### Tempting Alternatives and Why They Fail
- **Silent Dropping:** Explicitly violates processing SLAs requiring all records to be handled.
- **Signaling Upstream Producers to Block:** Kafka is a pull-based log architecture decoupled from producers; consumers cannot transmit reactive backpressure signals across the network protocol to pause upstream producers.
- **Expanding In-Memory Buffers:** In-memory queues merely delay exhaustion during sustained disparities. Adding consumer threads also fails when the real bottleneck is downstream database contention or external HTTP rate limits.

---

## Queue Backpressure: Managing Traffic Spikes at the Source

### The Problem
During peak demand, producers send 4,000 messages per minute into an SQS queue while consumers process only 200 per minute, building an 80,000-message backlog and pushing the downstream database to 95% CPU utilization.

### Recommended Solution: Throttle Ingestion at the Producer Level
Apply rate limiting (via token bucket, sliding window, or concurrency controls) at the producer layer feeding the queue. Because user checkouts are acknowledged upon initial write before asynchronous emitter jobs push downstream work, throttling the internal emitter balances the queue intake with database capabilities without harming client checkouts.

### Tempting Alternatives and Why They Fail
- **Horizontal Consumer Scaling:** When the bottleneck is database write capacity, spinning up extra workers overloads the database connection pool, driving database CPU to failure and increasing costs.
- **Visibility Timeout Adjustments and DLQs:** Visibility timeouts and dead-letter queues mitigate poison-pill messages and double processing; they cannot resolve continuous intake deficits.
- **SQS Delay Queues:** Postponing message visibility does not reduce message volume; it converts continuous over-saturation into grouped, spiky arrivals.

| Mitigation Approach | Fixes Root Imbalance? | Database Protected? | Operational Cost Impact |
| :--- | :--- | :--- | :--- |
| **Consumer Scaling** | No (moves bottleneck to DB) | No (escalates CPU crash) | Increases compute bills |
| **DLQ / Visibility** | No (handles poison pills only) | No | Neutral |
| **Delay Queues** | No (creates bursty spikes) | No | Neutral |
| **Producer Throttling** | **Yes** | **Yes** | **Minimal** |

---

## Release Safety: Rolling Out Irreversible Write Paths

### The Problem
Deploying a critical payment rewrite replacing standard credit card processing with a 3D-Secure workflow at 3,000 RPS. Charges cannot be automatically reversed if errors occur, making canary failures costly.

### Recommended Solution: Targeted Feature Flags
Deploy the updated codebase across 100% of the fleet in an inactive state behind a dynamic feature toggle. Route traffic incrementally based on client identifier or tenant tier (internal staff $\to$ low-tier users $\to$ enterprise), maintaining the legacy execution branch as a live fallback. Rollbacks execute instantly via configuration adjustments without redeploying code or cycling instances.

### Tempting Alternatives and Why They Fail
- **Canary Deploys:** Canaries partition traffic by random request percentages rather than customer boundaries. A high-frequency customer hitting the canary can experience duplicate faulty transactions before aggregate error dashboards alert. Furthermore, monetary bugs often return valid HTTP 200 responses with improper values, evading automated threshold triggers.
- **Blue/Green Deployments:** Cutover directs 100% of live traffic to the new branch instantly. Incoming webhook receipts from payments initiated on the old environment may encounter the new environment unexpectedly, resulting in race conditions.
- **Rolling Deployments:** Runs heterogeneous versions concurrently during the migration window, creating state desynchronization between initial order requests and subsequent confirmation callbacks.

---

## Multi-Tenant Isolation: Containing Noisy Neighbors Efficiently

### The Problem
A shared multi-tenant database using a shared table and schema model experiences database-wide lockups when an unpaid tenant runs an intensive batch export, stalling transactions for paying enterprise accounts.

### Recommended Solution: Middleware Routing Bridge (Hybrid Model)
Implement a dynamic tenant resolution layer that routes connections based on customer tier:
1. **Free / Low-Tier:** Pooled into a shared database.
2. **Growth / Mid-Tier:** Schema-per-tenant on a shared hardware cluster.
3. **Enterprise Tier:** Dedicated standalone database clusters with independent hardware and connection limits.

A central registry translates `tenant_id` to its dedicated connection profile at runtime. Noisy neighbors on free plans only impact other free tenants, enterprise hardware is strictly isolated, and tenants can be promoted across tiers without code rewrites.

### Tempting Alternatives and Why They Fail
- **Row-Level Security (RLS) with Query Quotas:** RLS and soft query caps operate inside the same database engine. Unconstrained connections, WAL saturation, and buffer pool eviction from large queries continue to degrade other tenants.
- **Universal Schema-Per-Tenant:** Running migrations across hundreds of individual schemas causes extensive DDL locks, bloats shared catalog metadata, and rapidly exhausts connection pool capacity.
- **Full Silo Model for All Tenants:** Provisioning isolated infrastructure for thousands of free or low-margin tenants leads to excessive infrastructure expenses before realizing commercial returns.

---

## Decision Cheatsheet

| Symptom / Architecture Scenario | Underlying Failure | Recommended Pattern |
| :--- | :--- | :--- |
| Downstream crashes at calendar minute resets despite legitimate RPS | Boundary burst vulnerability in fixed windows | **Token Bucket Rate Limiting** |
| Slow external API monopolizes connection pool, taking down healthy endpoints | Unbounded dependency delay across shared resources | **Bulkhead Pool + Circuit Breaker** |
| Kafka consumer lag grows uncontrollably; cannot drop messages | Processing rate mismatch in decoupled log streams | **Ingestion Ceiling + Overflow Topic Shedding** |
| Queue backlog rises sharply; downstream database reaches resource limits | Producer rate outstrips fixed persistence capacity | **Producer Ingestion Throttling** |
| High-risk deploy touches irreversible operations (e.g., payments) | Request-based rollouts lack identity context and fail silently | **Feature Flags with User Segmentation** |
| Free-tier bulk operations interrupt high-value enterprise transactions | Resource contention on unified multi-tenant database instances | **Middleware Routing Bridge (Hybrid Tiering)** |

---
*Source: Summary in our own words of scenario days 03, 14, 17, 20, 25, 51 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
