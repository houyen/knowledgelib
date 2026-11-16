---
id: software/system-design/book-60-days/idempotency-and-payment-correctness
canonical_question: How should distributed payment architectures handle idempotency, concurrent wallet updates, webhook retries, and read-after-write replication lag?
aliases:
- payment idempotency key architecture
- prevent duplicate payment charges
- webhook retry idempotency pattern
- optimistic locking wallet balance overspend
- payment confirmation read replication lag
- distributed transaction idempotency design
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 04, 11, 39, 57, 59 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Resilient Payment Architecture: Idempotency, Concurrency, and Consistency

## TL;DR
External payment operations require client-managed idempotency keys stored alongside complete responses to survive client retries and dropped connections. Inbound webhooks must decouple receipt from processing by verifying signatures and queuing raw events before acknowledging the provider. Account balances under typical contention should use optimistic locking with version checks instead of blocking locks, while read-after-write lag on critical confirmation flows is solved by surgically routing status checks directly to the primary database.

## Client-Side Retries and Duplicate Charge Prevention

### The Problem
A client experiences a network timeout during checkout and retries the request, leading to multiple independent API executions against upstream gateways and duplicate credit card charges.

### Recommended Solution
Require an `Idempotency-Key` HTTP header containing a client-generated UUID, and cache the resulting HTTP status code and response body in durable storage.

The client defines the logical intent of the transaction and attaches the same UUID to every retry attempt. Upon receiving a request, the server atomically creates a pending record for the key. If a subsequent request arrives while the original is still executing, the server either holds the connection or returns an HTTP 409 conflict. Once processing succeeds, the server stores the full gateway response against the key. Any later retry with that key immediately returns the cached response without touching external payment processors or appending duplicate ledger rows.

### Traps and Failure Modes
- **Database unique constraint on `(orderId, amount)`:** Fails because database boundaries do not govern external HTTP side effects. If the external gateway call precedes the database insert, duplicate charges occur before the constraint can abort the second write. If the insert precedes the charge, an application crash between the insert and the external call leaves a phantom payment record with no money transferred.
- **Distributed locking (e.g., Redis `SETNX`):** Protects only against concurrent, overlapping executions. If a network blip drops a successful HTTP response, the client retries after the lock has been released, causing a second charge.
- **SERIALIZABLE isolation level:** Confines correctness to database state. Rolling back a serialized transaction cannot retract an HTTP POST already received and processed by an external gateway.

| Strategy | Prevents Concurrent Races | Prevents Sequential Retries | Surrounds External Side Effects | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Idempotency-Key Cache (Recommended)** | Yes (via pending state) | Yes (cached response) | Yes | Low |
| **Unique DB Constraint** | No (side effect leaks) | No (side effect leaks) | No | Minimal |
| **Distributed Lock** | Yes | No (fails after release) | Partial | Medium |
| **SERIALIZABLE Isolation** | Yes (DB only) | No | No | High |

## Webhook Ingestion Under Load and Out-of-Order Retries

### The Problem
Payment gateway webhooks trigger retries due to local processing delays or deployment restarts, resulting in concurrent execution races and out-of-order state overwrites.

### Recommended Solution
Verify the webhook HMAC signature immediately, return an HTTP 200 acknowledgment, and push the raw event payload onto an internal message queue (such as Amazon SQS, Apache Kafka, or Redis Streams) for asynchronous consumption.

Payment providers enforce strict timeout windows (typically around 10 seconds). Complex tasks like fraud evaluation, database writes, and transactional email dispatch must be kept off the inbound HTTP thread. Validating the cryptographic signature takes under 5 milliseconds, allowing the endpoint to return an HTTP 200 in approximately 8 milliseconds. Once persisted in a durable broker, events remain protected against application pod restarts and database latency spikes. Worker processes handle domain mutations using state-machine transitions that reject invalid out-of-order events (such as ignoring a `charge.succeeded` event if the entity has already processed `charge.refunded`).

### Traps and Failure Modes
- **Synchronous deduplication table:** Checking event IDs against a relational database inside the HTTP request does not fix the root issue. Slow writes and deployment restarts still exceed the provider's timeout window, triggering continuous redelivery.
- **Inbound retry policies with DLQs:** Inbound delivery retries and backoff schedules are already executed by the payment gateway. Building retry loops at the ingestion endpoint confuses inbound transport with downstream worker processing.
- **Sequence numbers and reorder buffers:** Webhook providers rarely emit continuous, gapless sequence numbers. A missing or filtered event causes a reorder buffer to stall indefinitely. Domain-level state machines handle out-of-order arrivals and lost intermediate events gracefully.

| Architecture | HTTP Latency | Resilience to DB Spikes | Handles Ordering Issues | Provider Timeout Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Sync Ack + Async Queue (Recommended)** | <10ms | High (isolated) | High (state machine workers) | Negligible |
| **Synchronous Dedup Table** | 50ms–12s | None (blocks on DB) | Low | High |
| **Inbound Retries + DLQ** | High | Low | Low | High |
| **Reorder Buffers** | Variable | Low | Fragile (hangs on gaps) | High |

## Idempotency Key Generation Strategies

### The Problem
Selecting the ownership model and generation mechanism for idempotency tokens across unreliable networks and heterogeneous consumers.

### Recommended Solution
Use client-generated UUIDs scoped by account for public payment APIs; adopt the transactional outbox pattern with idempotent consumers for high-throughput internal distributed pipelines.

External clients hold the business intent: only the caller knows whether a repeated request is an intentional duplicate purchase or a network-forced retry. Clients generate a UUID before dispatching the request. The server registers the token with a 24-to-72 hour time-to-live, atomically marking it pending via `SET NX`, and binds the token scope to `(customer_id, key)` to avoid cross-tenant collisions. In complex, high-scale architectures (such as 10,000 transactions per second), pairing an outbox table with primary database writes ensures exactly-once event publication without relying on separate distributed caching infrastructure.

### Traps and Failure Modes
- **Deterministic business field hashing:** Hashing composite attributes like `sha256(customer_id + order_id + amount)` mistakenly blocks valid repeat purchases (such as an immediate reorder following a refund). Furthermore, subtle changes in JSON key serialization order between client SDK releases silently alter the computed hash and destroy deduplication guarantees.
- **Mandatory server-generated tokens (`/payments/init`):** Requiring clients to fetch a token before payment introduces an extra network roundtrip. On flaky mobile connections, this creates two independent failure points, multiplying the probability of orphaned states.

| Strategy | Best Use Case | Operational Overhead | Failure Mode Risk |
| :--- | :--- | :--- | :--- |
| **Client-Generated UUID (Recommended)** | Public & Mobile APIs | Low (Redis / DB key store) | Client sending malformed keys |
| **Transactional Outbox** | High-throughput distributed systems | Medium (worker infra) | Polling or CDC latency |
| **Server-Generated Tokens** | Regulated, internal service-to-service | Medium (two-phase roundtrips) | Multiplied network timeouts |
| **Deterministic Hashing** | Batch jobs, cron dedup | Minimal | Collisions on valid repeat orders |

## Concurrent Balance Deductions and Overspend

### The Problem
Simultaneous requests read the same initial wallet balance and process concurrent deductions, causing the account balance to fall below zero.

### Recommended Solution
Implement optimistic concurrency control by checking the row version during the atomic database update.

The application reads the account balance alongside an integer `version` field. When persisting the deduction, the update statement targets that exact version while incrementing it:
```sql
UPDATE wallets
SET balance = balance - 150, version = version + 1
WHERE id = :wallet_id AND version = :read_version AND balance >= 150;
```
If a competing update commits first, the `WHERE` clause matches zero affected rows. The application detects the conflict without holding long-lived database locks and retries the flow. Under standard traffic profiles where conflicts are infrequent, this delivers high throughput without locking overhead.

### Traps and Failure Modes
- **Pessimistic locking (`SELECT FOR UPDATE`):** Holds an exclusive row-level lock across the entire transaction. Under heavy traffic directed at shared or hot balances, incoming transactions serialize, connection pools saturate, and lock-wait timeouts cascade.
- **Standard MVCC under READ COMMITTED:** PostgreSQL's default isolation level refreshes snapshots at each SQL statement. Two concurrent transactions can both read a $200 balance, confirm sufficient funds, and proceed with deductions, causing a silent double spend.
- **SERIALIZABLE transaction isolation:** Rather than executing serially, engines use serializable snapshot isolation to monitor dependency graphs. High write volumes provoke frequent serialization failures and retry storms, imposing a major throughput penalty.

| Concurrency Control | Lock Overhead on Reads | Contention Scalability | Double-Spend Protection | Implementation Effort |
| :--- | :--- | :--- | :--- | :--- |
| **Optimistic Locking (Recommended)** | None | High (low-to-moderate conflict) | Complete | Low |
| **Pessimistic (`FOR UPDATE`)** | High (exclusive lock) | Poor (bottlenecks on hot rows) | Complete | Low |
| **Default MVCC (READ COMMITTED)** | None | High | None (lost updates occur) | None |
| **SERIALIZABLE Isolation** | Low | Low (abort storms at scale) | Complete | Low |

## Read Consistency Across Replicas After Payment

### The Problem
A user completes a payment and is redirected to an order status screen that displays "Pending" or "Failed" because the read query hits an asynchronous replica experiencing replication lag.

### Recommended Solution
Enforce read-your-writes consistency by routing payment confirmation reads back to the primary database, while keeping generic browsing traffic on asynchronous replicas.

Payment verification and checkout completion flows account for a tiny fraction (typically under 0.1%) of total platform read operations. Injecting contextual routing flags (or session-based middleware) to direct read-your-writes requests to the primary database provides guaranteed consistency where stale data causes user confusion, while keeping the broader replica pool offloaded.

### Traps and Failure Modes
- **Synchronous replication (`synchronous_commit = on`):** Forces the primary to block writes until at least one replica confirms disk flush. Write latency becomes tethered to network variability and the slowest replica, and an unhealthy replica can stall writes entirely.
- **Semi-synchronous replication:** The primary confirms writes when a replica writes the change to its relay log, rather than when the data is applied. A read against that replica can still retrieve stale records before the relay log executes.
- **Sleep-based delays (e.g., waiting 500ms):** Hardcoding sleep intervals adds latency to healthy requests, yet still fails during traffic spikes, table vacuums, or network degradations where replication lag exceeds the static sleep duration.

| Routing / Replication Strategy | Write Latency Impact | Immediate Read Consistency | Primary DB Load | Availability Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Route for Critical Reads (Recommended)** | None | Guaranteed | Minimal (+0.1% reads) | Low |
| **Synchronous Replication** | High (roundtrip bound) | Guaranteed | None | High (slow replica halts writes) |
| **Semi-Synchronous Replication** | Moderate | Not guaranteed (relay log gap) | None | Moderate |
| **Client/Server Sleep Padding** | None | Fragile (fails on lag spikes) | None | Low (wastes user time) |

## Decision cheatsheet

| Scenario / Symptom | Root Cause | Architectural Pattern | Key Caveat / Detail |
| :--- | :--- | :--- | :--- |
| Duplicate gateway charges on client retry | Network drops response; client repeats untracked POST | Client-generated `Idempotency-Key` + response caching | Write key as `pending` before charging; cache full response body and code |
| Webhooks time out under load; duplicate emails sent | Synchronous processing exceeds gateway timeout (~10s) | Signature verification + immediate ACK + message broker | Process domain updates via state machines to handle out-of-order events |
| Identical requests generate conflicting duplicate records | Missing or ambiguous idempotency token strategy | Client UUID for external APIs; Outbox pattern for distributed services | Scope keys to `(customer_id, key)`; avoid deterministic hashing of business fields |
| Wallet balance drops below zero under concurrent spend | Simultaneous reads pass balance check before writing deduction | Optimistic locking via version column (`WHERE version = :v`) | Check rows affected; retry on zero. For ultra-hot keys, use Redis atomic decrements |
| Customer sees "Unpaid" immediately after successful checkout | Read request directed to replica experiencing replication lag (80–300ms) | Read-your-writes consistency directed to the primary database | Scope primary reads strictly to post-write verification paths (approx. 0.1% of reads) |

---
*Source: Summary in our own words of scenario days 04, 11, 39, 57, 59 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
