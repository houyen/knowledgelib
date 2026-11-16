---
id: software/system-design/book-60-days/cqrs-event-sourcing-and-streaming
canonical_question: How do you select the appropriate architectural patterns for data modeling, state reconstruction, stream processing, and client streaming when encountering structural and latency mismatches?
aliases:
- CQRS vs read replicas
- event sourcing vs CDC audit log
- Flink vs Spark streaming latency
- SSE vs WebSockets for LLM chat
- real-time streaming transport selection
- read write schema decoupling
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 09, 21, 33, 41 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Architectural Decoupling: Data Models, State Reconstruction, Stream Processing, and Client Transports

## TL;DR
Architectural failures occur when engineers apply compute scaling or protocol band-aids to structural shape and latency mismatches. When read schemas demand denormalization while writes require relational consistency, separate the models via CQRS instead of duplicating expensive joins across read replicas. When business intent and temporal state reconstruction are required, make immutable domain events the source of truth rather than trying to infer meaning from mutated database rows. For real-time streaming down to the client or through the processing pipeline, choose engines and protocols whose physical execution matches the workload's directionality and event latency boundaries.

## Scenario 1: Decoupling Read and Write Shapes at Scale
**Problem:** A relational database handling 8,000 writes/min and 40,000 reads/min suffers from 85% CPU spikes because operational writes demand strict normalization while reporting dashboards execute repetitive 7-table joins across the same tables.

### Recommended Solution: Full CQRS
Implement Command Query Responsibility Segregation (CQRS) to isolate the write domain from read projections. The write model remains in normalized PostgreSQL tables protected by foreign keys, constraints, and ACID guarantees. As writes occur, an asynchronous projector (driven by the transactional outbox pattern or change data capture) populates a flattened read store—such as Elasticsearch or a denormalized PostgreSQL view table. 

This eliminates online join execution entirely: dashboard order cards render via single-key lookups against precomputed views. Eventual consistency introduces a brief propagation delay (typically under a few hundred milliseconds), which is completely acceptable for roughly 95% of read volume like dashboards and analytics. For the remaining 5% of operations demanding immediate read-your-own-writes guarantees (such as instant checkout confirmation screens), clients query the write model directly.

### Tempting Alternatives and Failure Modes
*   **Read Replicas:** Adding replicas redistributes CPU utilization across more nodes but does not address query shape. The expensive 7-table join continues to run on every read, merely shifting hardware expenses and postponing query exhaustion until read volume scales further.
*   **Denormalizing the Write Model:** Inlining line items and customer records directly into orders avoids read joins but introduces severe write amplification at 8,000 writes/min. Simple address or item adjustments require updating extensive historical records, while the schema becomes rigid and difficult to alter without massive table rewrites.
*   **GraphQL with DataLoader:** DataLoader batches client-side N+1 round trips across microservices or REST endpoints; it cannot optimize multi-table joins executed internally by the relational database engine.

| Approach | Primary Mechanism | Trade-Off / Failure Point | Optimal Fit |
| :--- | :--- | :--- | :--- |
| **Full CQRS** | Normalized write DB + asynchronous projection to flattened read store | Eventual consistency lag between read and write tiers | Disparate schema requirements between reads and writes |
| **Read Replicas** | Asynchronous replication of identical relational schema | Identical join cost multiplied across additional hardware | High read volume where query schemas are already efficient |
| **Write Denormalization** | Flattening source relational tables | Severe write amplification and schema migration bottlenecks | Read-heavy domains with near-zero write updates |
| **GraphQL + DataLoader** | Request-level query batching and in-memory deduplication | Fails to optimize database-internal relational joins | Client-to-API N+1 network request waterfalls |

## Scenario 2: Reconstructing State and Business Context from Mutation History
**Problem:** An e-commerce service handling 200 writes/sec overwrites database records on state changes, causing inconsistent historical totals during an audit of Order #8471 without any verifiable paper trail of how the discrepancy occurred.

### Recommended Solution: Event Sourcing
Transition the primary persistence model from mutable rows to an append-only event store. Instead of persisting only the current state of an order, the system records every lifecycle transition as a first-class, immutable business event (`OrderPlaced`, `CouponApplied`, `PaymentCaptured`, `ItemSubstituted`, `RefundInitiated`). 

Current operational state is derived by replaying these events sequentially from inception or from periodically generated snapshots. For disputes and audits, the full timeline of Order #8471 is precisely reconstructible at any arbitrary point in time. Crucially, the system preserves high-fidelity business context—recording not merely that an invoice total dropped, but the exact intent that caused the adjustment.

### Tempting Alternatives and Failure Modes
*   **Change Data Capture (CDC):** Streaming database row diffs via CDC (such as Debezium to Kafka) provides an operational audit trail, but it records physical state deltas rather than intent. Knowing a column changed from 89.99 to 79.99 does not capture whether the reduction resulted from a promotional code, a price override, or a tax exemption.
*   **Database Triggers (`audit_log`):** Trigger-based shadow writing treats auditing as a secondary side effect. Triggers are routinely disabled during bulk data imports, schema migrations, or maintenance operations, leaving unrecoverable gaps in audit records.
*   **Dual-Writing:** Writing concurrently to both a current-state table and an event log without distributed transaction boundaries guarantees drift. Any network partition, crash, or memory exhaustion during the split write leaves the event trail desynchronized from live state.

| Approach | Storage Strategy | Context Captured | Core Weakness |
| :--- | :--- | :--- | :--- |
| **Event Sourcing** | Append-only event stream as the authoritative record | Full business intent and state transition rationale | Requires learning event-driven paradigms and snapshot management |
| **CDC on Database** | Streaming low-level row-level mutations | Value deltas without domain meaning | Cannot explain why an operational change occurred |
| **DB Triggers** | Shadow table populated by internal database hooks | Row snapshot at execution time | Silently bypassed by administrative scripts and migrations |
| **Dual-Write** | Application writes to table and audit log sequentially | Variable depending on implementation | Inevitable state divergence when one write operation fails |

## Scenario 3: Real-Time Fraud Detection Under Sub-Second SLAs
**Problem:** A transaction pipeline peaking at 8,000 events/sec must evaluate transactions against a Python-based fraud model and publish signals to DynamoDB within a strict 500ms end-to-end SLA, moving away from existing nightly Spark batch jobs.

### Recommended Solution: Apache Flink
Deploy Apache Flink as a dedicated stream processing engine. Flink operates on continuous, true event-by-event pipelined execution rather than micro-batches, delivering sub-50ms end-to-end latencies at 8,000 events/sec. 

Flink natively handles distributed clock skew and out-of-order transaction deliveries using watermarks, ensuring fraud scoring across distributed payment processors remains accurate. It guarantees exactly-once processing across worker failures and integrates cleanly with Python data science models via PyFlink or low-latency sidecar processes without requiring external network hops for stateful operators.

### Tempting Alternatives and Failure Modes
*   **Spark Structured Streaming:** Although convenient for teams already operating Spark, Structured Streaming runs on a micro-batch model. Gathering events into discrete time windows inevitably pushes processing intervals into the 100ms–5s range under production volumes, regularly breaching the 500ms SLA during peak traffic bursts.
*   **Kafka Streams:** While offering sub-10ms event-by-event processing, Kafka Streams is designed as a JVM-embedded client library. Because the machine learning scoring logic is implemented in Python, embedding processing in the JVM requires an external network call to a Python evaluation service for every transaction, adding network overhead.
*   **Accelerated Batch Windows (1-Minute Intervals):** Truncating batch execution windows cannot achieve sub-second targets. The processing delay is fundamentally bounded by the batch collection interval, leaving latency two orders of magnitude above the 500ms SLA.

| Engine | Execution Primitive | Typical Processing Latency | Language Ecosystem Integration |
| :--- | :--- | :--- | :--- |
| **Apache Flink** | Continuous event-by-event | Sub-50ms | JVM core with native PyFlink support |
| **Kafka Streams** | Continuous event-by-event | Sub-10ms | Strictly JVM-embedded application library |
| **Spark Streaming** | Micro-batch collection | 100ms to several seconds | Shared Spark engine APIs (Python/Scala) |
| **Batch Reduction** | Scheduled macro-batches | Equal to collection interval | Agnostic |

## Scenario 4: Low-Overhead Unidirectional Streaming for Browser Clients
**Problem:** An interactive web chat service must stream 40 text tokens per second (5–20 bytes each) to 50,000 concurrent browser clients over FastAPI and an Application Load Balancer, requiring transparent reconnection handling over mobile networks.

### Recommended Solution: Server-Sent Events (SSE)
Utilize Server-Sent Events over standard HTTP (`text/event-stream`). The traffic model is strictly unidirectional: the client submits prompts via standard HTTP POST requests, while the server pushes generated tokens back to the client. SSE matches this communication shape without protocol translation.

Browsers provide native client management through the `EventSource` interface, which includes built-in auto-reconnection and state resumption via the `Last-Event-ID` header. If a mobile connection drops, the browser automatically reconnects and communicates the last observed token offset, allowing the backend to resume streaming cleanly. Operating over plain HTTP eliminates sticky session mandates on the load balancer, simplifies authentication, and bypasses proxy negotiation issues.

### Tempting Alternatives and Failure Modes
*   **WebSockets:** WebSockets establish a full-duplex TCP connection, adding unnecessary overhead for half-duplex text streaming. At 50,000 concurrent connections, WebSockets necessitate ALB sticky sessions, increase memory consumption for idle uplink buffers, and require custom implementations for heartbeat management, connection drop detection, and token replay.
*   **gRPC Server Streaming:** Web browsers cannot natively establish raw HTTP/2 gRPC framing. Adopting gRPC requires deploying an intermediary proxy (such as Envoy) to translate gRPC-Web into gRPC and forces the frontend to unpack binary Protobuf frames simply to display raw UTF-8 text strings.
*   **Long Polling:** At 40 tokens per second across 50,000 active users, polling generates up to 2,000,000 HTTP requests per second. The associated HTTP header parsing and connection handshakes consume immense server and network capacity.

| Transport | Communication Direction | Browser Support | Reconnection Mechanism |
| :--- | :--- | :--- | :--- |
| **Server-Sent Events** | Server-to-client unidirectional | Native (`EventSource`) | Built-in via standard `Last-Event-ID` tracking |
| **WebSockets** | Full-duplex bidirectional | Native (`WebSocket`) | Manual application-level heartbeat and replay logic |
| **gRPC-Web** | Server streaming or unary | Requires translation proxy | Application-level retry and stream reconstruction |
| **Long Polling** | Unidirectional pull | Native (`fetch`) | Re-executes complete HTTP request lifecycle per message |

## Decision cheatsheet

| Operational Symptom or Requirement | Recommended Pattern | Core Decision Rule |
| :--- | :--- | :--- |
| Read queries require complex multi-table joins while writes require normalized transactional integrity | **CQRS** | Separate read and write data stores; project writes asynchronously into flat read-optimized views. |
| Read load overwhelms the primary database, but queries are simple single-table or indexed lookups | **Read Replicas** | Retain identical schemas and distribute uniform relational queries across read replicas. |
| System must explain why values changed, settle audits, or reconstruct historical state | **Event Sourcing** | Persist immutable domain events as the source of truth; project current state via event replays. |
| Downstream caches or analytics need live database updates without modifying the source application | **Change Data Capture** | Stream physical row-level mutation logs to message brokers; accept the absence of business intent. |
| Stateful stream analytics must process high-volume events under a strict sub-second SLA (<500ms) | **Apache Flink** | Choose continuous event-by-event stream processing with native out-of-order watermark handling. |
| Near real-time pipelines can tolerate 1–5 second processing latencies with existing batch tooling | **Spark Structured Streaming** | Use micro-batch processing engines when existing infrastructure and team expertise prioritize batch code reuse. |
| Browser client requires high-frequency, server-to-client text or token streams | **Server-Sent Events** | Use HTTP `text/event-stream` for unidirectional pushes with native browser reconnection capabilities. |
| Interactive client requires low-latency, bidirectional, full-duplex communication (e.g., multiplayer data) | **WebSockets** | Incur protocol upgrade and sticky session overhead only when concurrent two-way data streaming is essential. |

---
*Source: Summary in our own words of scenario days 09, 21, 33, 41 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
