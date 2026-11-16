---
id: software/system-design/bytebytego-archive-2025/kafka-rabbitmq-messaging-streaming
canonical_question: How do message queues, pub/sub brokers, and distributed streaming platforms differ, and when should each be used?
aliases:
- kafka vs rabbitmq
- sqs vs sns vs eventbridge vs kinesis
- message broker vs event streaming
- batch vs stream processing architecture
- choosing an asynchronous messaging pattern
- how rabbitmq and kafka handle messages
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Asynchronous Messaging, Queues, and Event Streams: Architecture and Selection Guide

## TL;DR
Distributed messaging solutions divide into discrete task queues, publish/subscribe routers, and append-only distributed event logs. Traditional brokers such as RabbitMQ and AWS SQS focus on task distribution and remove messages once processed, while pub/sub systems like SNS and EventBridge distribute events to multiple endpoints using topic fanout or payload-filtering rules. In contrast, distributed log engines like Apache Kafka and AWS Kinesis retain ordered, replayable event streams across partitions, enabling continuous real-time processing and independent consumption at scale.

## Core Processing Paradigms: Batch vs. Stream

Distributed systems process information across two primary operational modes:

* **Batch Processing:** Gathers transactions into bounded chunks and evaluates them at predetermined intervals. It focuses on high-volume throughput and historical precision, making it ideal for aggregate reporting, auditing, and offline computational workloads.
* **Stream Processing:** Ingests and evaluates unbounded sequences of events on an ongoing basis. It minimizes latency to deliver immediate responses, driving operational live dashboards, instant alerts, fraud detection, and dynamic recommendations.

Choosing between batch and streaming depends on whether the system requires historical accuracy over an accumulation period or instantaneous action as individual state changes happen.

## Point-to-Point Message Queues: RabbitMQ and AWS SQS

Message queues decouple producers from consumers by holding discrete messages until a worker consumes and processes them.

### RabbitMQ Internals
RabbitMQ operates as a centralized broker where producers send messages to internal routing components called exchanges. Exchanges do not hold data directly; instead, bindings map exchanges to destination queues using routing keys. 

Routing behaviors depend on the exchange type:
* **Direct Exchange:** Matches the message routing key identically to the binding key assigned to a queue.
* **Topic Exchange:** Evaluates wildcards and pattern expressions within the routing key to route messages to one or more matched queues.
* **Fanout Exchange:** Ignores routing keys entirely and replicates the payload across every queue bound to the exchange.

Once routed to a queue, consumers pull the messages. As soon as a consumer acknowledges successful handling, RabbitMQ deletes the message from storage. This pattern optimizes the broker for task allocation, work distribution, and stateful delivery guarantees.

### AWS SQS
AWS SQS provides a serverless, managed message queue designed for worker pipelines. It excels when isolated jobs require execution by a single consumer process—such as queuing background image conversions or transcode tasks—without requiring manual management of broker clustering.

## Publish/Subscribe and Rule-Based Event Routing: SNS and EventBridge

When a single producer event must notify multiple decoupled services simultaneously, simple point-to-point queues become insufficient.

* **AWS SNS (Simple Notification Service):** A fully managed publish/subscribe engine centered around topics. When publishers issue a message to an SNS topic, the service performs an uninspected fanout broadcast, pushing that notification out to many heterogeneous subscriber endpoints concurrently, including AWS Lambda functions, SQS queues, and HTTP or email endpoints.
* **AWS EventBridge:** A serverless enterprise event bus tailored for reactive system architectures. Unlike simple fanout topics, EventBridge inspects the schema and payload of incoming events, applying granular rules and filters to decide which downstream microservices or AWS resources should receive the record. This makes EventBridge the standard tool for choreographing cross-system events, such as orchestrating downstream services when a customer registers.

## Distributed Streaming Logs: Apache Kafka and AWS Kinesis

Distributed streaming platforms fundamentally differ from traditional message brokers: they persist an immutable, ordered sequence of records on disk rather than deleting messages upon delivery.

### Apache Kafka Architecture
Kafka structures incoming streams as topics split across partitions to achieve parallel execution and fault tolerance:
1. **Producers and Serialization:** Client applications convert objects into raw byte payloads via serializers. A partitioner assigns each record to a specific partition based on hashing keys or round-robin strategies.
2. **Broker Clusters and Storage:** Kafka brokers accept records and append them to the end of partition commit logs. Data in each partition remains ordered and immutable. Brokers replicate partitions across distinct cluster nodes to guarantee high availability.
3. **Cluster Coordination (KRaft):** Kafka employs a controller quorum built on the KRaft consensus protocol to govern metadata, elect partition leaders, and maintain cluster-wide synchronization without external orchestration layers.
4. **Consumer Groups and Offsets:** Downstream systems subscribe through consumer groups. Kafka allocates partitions among group members so that each consumer ingests from dedicated partitions without contention. Consumers advance and commit an offset marker as they read. Because messages remain stored according to time- or size-based retention policies, consumers can reset their offsets to rewind, replay, and reprocess historical streams independently.

### AWS Kinesis Data Streams
AWS Kinesis provides managed streaming infrastructure equivalent in concept to Kafka's partitioned log design. It continuously ingests massive event streams—such as telemetry, infrastructure metrics, or real-time website clickstreams—and retains the ordered data for near-real-time parallel processing engines.

## Architectural Comparisons

### Kafka vs. RabbitMQ

| Architectural Dimension | Apache Kafka | RabbitMQ |
| :--- | :--- | :--- |
| **Data Structure** | Distributed, append-only commit log | Ephemeral FIFO message queues |
| **Persistence Model** | Retained by policy (time/size); never deleted by consumers | Removed from queue upon consumer acknowledgment |
| **Consumption Style** | Consumer pull via offset pointers; replayable | Consumer pull or broker push; destructive read |
| **Routing Flexibility** | Topic- and partition-level assignment | Flexible routing via exchanges (Direct, Topic, Fanout) |
| **Primary Workload** | High-throughput event streaming, analytics, event sourcing | Task distribution, command pipelines, complex routing |

### AWS Messaging Ecosystem Matrix

| Service | Architecture Pattern | Routing & Filtering Mechanism | Primary Workload |
| :--- | :--- | :--- | :--- |
| **AWS SQS** | Point-to-point queue | Single-queue polling | Decoupled worker jobs (e.g., media processing) |
| **AWS SNS** | Topic-based pub/sub | Broadcast fanout to subscribers | Multi-recipient alerting and notifications |
| **AWS EventBridge** | Serverless event bus | Declarative JSON payload filtering rules | Inter-service integration (e.g., user lifecycle events) |
| **AWS Kinesis** | Sharded streaming log | Partition key routing | Ingesting high-volume streams (e.g., clickstreams) |

## Common Mistakes

* **Treating Kafka as a Traditional Work Queue:** Attempting to implement per-message acknowledgment, individualized message routing, or dynamic single-item deletion inside Kafka causes complex anti-patterns; use standard queues like SQS or RabbitMQ for transient task distribution.
* **Treating RabbitMQ as an Event Sourcing Log:** Attempting to rewind and replay historical transactions in RabbitMQ fails because acknowledged messages are discarded immediately from the broker.
* **Using SQS When Multi-Service Fanout Is Needed:** Sending the same event to multiple independent microservices via a single point-to-point queue causes competing consumers to steal each other's jobs; broadcast via SNS or route via EventBridge into service-specific queues instead.
* **Relying on Batch Pipelines for Latency-Sensitive Actions:** Collecting data in periodic scheduled windows when downstreams require instantaneous reactions introduces avoidable latency; use stream processing for live metrics, dashboards, and automated fraud prevention.

---
*Source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
