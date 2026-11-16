---
id: software/system-design/book-60-days/distributed-coordination-and-messaging
canonical_question: How do you choose the right architectural patterns to handle distributed locks, event ordering, cross-service transactions, reliable messaging, async jobs, and heavy client compute?
aliases:
- distributed locking with fencing tokens
- message queue event ordering sqs fifo
- orchestration vs choreography sagas
- two generals problem idempotency key messaging
- polling vs websockets long running tasks
- offloading main thread web workers
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 06, 07, 10, 22, 40, 56 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Pragmatic Patterns for Distributed Systems and Asynchronous Workflows

## TL;DR
Default to the simplest operational boundary that avoids holding state across network boundaries. Enforce correctness at the destination data store using monotonically increasing fencing tokens or idempotency keys rather than relying on perfect locks or error-free network links. Use queue partition keys for entity sequencing, centralized orchestrators for multi-step transactional compensations, client polling for minutes-long background jobs, and background threads to prevent UI freezes.

---

## Distributed Locks for Scheduled Cron Jobs

**Problem:** Multiple instances grab the same cron trigger, but node crashes or garbage collection pauses outlast the lock's expiration, creating concurrent execution hazards.

### Recommended Pattern: Lock with Short TTL and Downstream Fencing Token
Acquire the lock with a brief time-to-live and obtain an incrementing sequence number (a fencing token). The underlying storage system, database, or external sink validates this token on every write and rejects updates bearing an identifier lower than the latest committed token. Because network partitions and process halts can silently strip ownership from an active process, safety cannot be guaranteed by the lock provider alone; the downstream storage target must serve as the final authority.

### Tempting Traps and Failure Modes
- **Multi-Node Redis Quorums (Redlock):** Acquiring locks across an odd number of independent nodes does not protect against execution pauses on the worker. If a thread stalls past lease expiration, another node wins the lock; when the original node wakes, it still issues uncoordinated writes unless fenced. It adds multi-cluster operational complexity without fixing the root pause issue.
- **Database Row Locks (`SELECT FOR UPDATE`):** Tying locks to long-running transactions starves the database connection pool. If jobs perform slow network requests or object storage writes, open transactions hold locks for dozens of seconds and exhaust connection limits.
- **Optimistic Concurrency at Write-Time:** Attempting an uncoordinated write and relying on uniqueness constraints fails whenever jobs execute non-reversible side effects prior to the database write, such as charging credit cards, sending emails, or issuing compute jobs.

| Approach | Resilience to GC/Stalls | Connection Overhead | Handles External Side Effects |
| :--- | :--- | :--- | :--- |
| **Fencing Token + Lease** | High (Sink verifies token) | Minimal | High |
| **Redlock (without token)** | Low (Silent lease loss) | High (Multiple clusters) | Poor |
| **Pessimistic DB Lock** | Medium (Fails on conn drop) | Critical bottleneck | Moderate |
| **Optimistic Concurrency** | None | Low | Fails (Runs work multiple times) |

---

## Event Ordering Across Message Queues

**Problem:** Rapid successive entity state updates on standard queues are pulled concurrently by separate workers, leading to out-of-order execution such as processing cancellations prior to creation.

### Recommended Pattern: FIFO Queue with Entity-Scoped Group Identifiers
Switch to a FIFO queue configuration and assign the entity identifier (e.g., `order_id`) as the message group key. The queue infrastructure guarantees strict in-order delivery for messages sharing an entity key while dedicating delivery to a single consumer at a time for that specific key. Throughput remains high because independent entities process concurrently across all available workers.

### Tempting Traps and Failure Modes
- **Consumer-Side Reorder Buffers:** Storing out-of-order events in memory until preceding messages arrive forces developers to replicate distributed broker semantics. You inherit edge cases around node crashes, memory consumption, missing message timeouts, and dead-letter handling.
- **Saga Orchestration:** Introducing a saga for single-entity state transitions turns asynchronous event ingestion into heavyweight, synchronous coordination. It introduces unnecessary latency and architectural coupling.
- **State Machine Event Versioning:** Rejecting stale state transitions without a full event-sourcing architecture drops required events. If a cancellation arrives first, a later creation event is rejected as invalid, leaving the data permanently corrupted.

| Approach | Implementation Effort | Crash Safety | Scalability |
| :--- | :--- | :--- | :--- |
| **FIFO Grouping (per entity)** | Low (Configuration change) | High (Managed by broker) | High (Fanned out by ID) |
| **Consumer Reorder Buffer** | High (Custom buffering logic) | Low (Volatile memory risk) | Moderate (Memory-bound) |
| **Saga Workflow** | High (Multi-step state machines)| High | Poor (Excess sync hops) |
| **Event Version Rejection** | Low | Low (Drops valid context) | High |

---

## Multi-Service Distributed Transactions

**Problem:** A multi-step transaction across separate microservice databases fails halfway through, stranding partial state across business boundaries.

### Recommended Pattern: Orchestration Saga
Implement a centralized state machine that sequentially invokes each participating service and tracks execution progress. When a step fails, the orchestrator triggers reverse compensating actions in strict reverse order to roll back state changes. This provides a single observable location to inspect failure points, monitor timeouts, and automate compensating calls without scattering business rules across systems.

### Tempting Traps and Failure Modes
- **Choreography Saga:** Relying on independent event reactions between services causes logic to fragment once workflows exceed a few steps. Diagnosing failures requires parsing logs across disparate event streams, and handling branched compensation logic creates cyclic dependencies between services.
- **Two-Phase Commit (2PC):** Third-party APIs (payment processors, third-party logistics) do not expose atomic transaction interfaces. Furthermore, holding locks across network boundaries during prepare phases severely degrades database throughput and increases vulnerability to network splits.
- **Transactional Outbox in Isolation:** The outbox pattern guarantees reliable message publishing from a local database commit, but it does not manage cross-system sequencing, state tracking, or backward compensation when a downstream step fails.

| Strategy | Observability | Failure Compensation | Third-Party API Fit |
| :--- | :--- | :--- | :--- |
| **Orchestration Saga** | High (Single state machine) | High (Automated rollback) | High |
| **Choreography Saga** | Low (Distributed event logs) | Complex (Scattered logic) | Moderate |
| **Two-Phase Commit (2PC)** | Moderate | Low (Holds network locks) | Unusable |
| **Outbox Alone** | High (Local table) | None (Transport only) | High |

---

## Reliable Asynchronous Inter-Service Messaging

**Problem:** Network timeouts when notifying downstream services leave the sender uncertain whether a call succeeded, risking duplicate actions on retries.

### Recommended Pattern: Message Queue with Consumer Idempotency Keys
Enqueue the event into an asynchronous broker offering at-least-once delivery, attaching a stable deduplication token (e.g., `payment_id:action:v1`). The consumer checks this token against an idempotency store within its local database transaction before applying updates. The queue handles network retries and absorption of service downtime, while consumer-side deduplication neutralizes duplicate deliveries.

### Tempting Traps and Failure Modes
- **Synchronous HTTP Retries:** Network timeouts often mask a completed operation whose confirmation response dropped in transit. Repeating HTTP calls without consumer deduplication triggers duplicate actions, while infinite retry loops amplify downstream resource exhaustion.
- **Distributed Two-Phase Commit:** Coordinating synchronous locks across service boundaries introduces a single point of failure at the coordinator and leaves resources locked if an endpoint hangs.
- **Transactional Outbox for Simple Queues:** While effective for strictly synchronizing local DB commits with event brokers, standing up outbox tables, change data capture processes, and cleanup scripts introduces unnecessary operational overhead when standard message queues and idempotency keys satisfy requirements.

---

## Status Tracking for Long-Running Async Tasks

**Problem:** Long-running backend processes outlast gateway connection timeouts, preventing clients from tracking task completion over simple synchronous HTTP calls.

### Recommended Pattern: Client-Driven Polling Endpoint
Return an accepted status immediately with a persistent task identifier, exposing a dedicated query endpoint (`/jobs/:id`) for status retrieval. The client queries the endpoint using exponential backoff until the task resolves. Polling is stateless, survives mobile client disconnections, scales independently behind caches, and avoids keeping long-running transport sockets active on the application tier.

### Tempting Traps and Failure Modes
- **Synchronous Connection Holding:** Holding open HTTP connections over multiple minutes triggers proxy and load balancer timeouts (typically 30–60 seconds), blocks web server worker threads, and provides no recovery mechanism if the client briefly drops connectivity.
- **Webhooks for Client Applications:** Webhooks require an accessible, static HTTPS callback URL, making them unviable for mobile devices or browsers operating behind NAT and firewalls.
- **WebSockets / Server-Sent Events:** Maintaining persistent connections for jobs that transition states only a few times over several minutes consumes server file descriptors and adds complex reconnect handling for minimal functional benefit.

| Mechanism | Infrastructure Complexity | Mobile/NAT Support | Connection Resource Usage |
| :--- | :--- | :--- | :--- |
| **Status Polling** | Minimal (Standard REST) | Universal | Low (Stateless requests) |
| **Synchronous Hold** | Minimal | Poor (Proxy timeouts) | High (Holds thread/socket) |
| **Webhooks** | High (Retry/signing infra) | Incompatible | Low |
| **WebSockets/SSE** | High (Connection brokers) | High | High (Continuous socket) |

---

## Heavy Client-Side Compute Offloading

**Problem:** Executing resource-intensive operations synchronously on the browser thread freezes the event loop, breaking page interactivity and driving up interaction metrics like INP.

### Recommended Pattern: Dedicated Web Workers
Execute heavy parsing, validation, and serialization routines within a Web Worker running on an isolated background thread. Passing large data structures using transferable buffers avoids serialization penalties while leaving the main JavaScript thread completely open to handle layout, user interactions, and rendering frames at 60fps.

### Tempting Traps and Failure Modes
- **Time-Slicing with `requestIdleCallback`:** Breaking loops into slices keeps frames responsive but severely inflates overall processing duration due to constant context yielding. Furthermore, idle callbacks are deprioritized and can stall entirely under active system load.
- **SharedArrayBuffer with Atomics:** Achieving zero-copy sharing via atomic memory buffers forces site-wide implementation of cross-origin isolation headers (COOP and COEP), which breaks third-party script integrations, payment frames, and embedded media.
- **WebAssembly on the Main Thread:** WebAssembly increases raw execution speed, but running it synchronously on the primary UI thread still freezes page rendering for the duration of the calculation.

---

## Decision Cheatsheet

| Symptom / Requirement | Recommended Pattern | Antipattern to Avoid |
| :--- | :--- | :--- |
| Job runs concurrently after worker stall or GC pause | Distributed lock lease with **sink-checked fencing token** | Redlock without write-time token validation |
| Queue workers process entity lifecycle events out of order | **FIFO queue with entity group keys** (`order_id`) | In-memory consumer reorder buffers |
| Multi-service checkout flow fails midway and requires rollback | **Centralized orchestration saga** | Distributed event-choreography chains |
| Inter-service notifications intermittently fail on network timeouts | **Queue at-least-once delivery + consumer idempotency key** | Synchronous HTTP retry loops without deduplication |
| Multi-minute operations exceed API gateway limits | **Asynchronous job status polling** with backoff | Synchronous HTTP connection holds or WebSockets |
| Large browser operations cause frame drops and UI freezes | **Dedicated Web Worker** via background thread | Main-thread time-slicing or synchronous WebAssembly |

---
*Source: Summary in our own words of scenario days 06, 07, 10, 22, 40, 56 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
