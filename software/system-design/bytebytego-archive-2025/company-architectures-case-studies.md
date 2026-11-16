---
id: software/system-design/bytebytego-archive-2025/company-architectures-case-studies
canonical_question: How do large-scale tech companies evolve their architectures, tech stacks, and infrastructure to handle hypergrowth?
aliases:
- scaling monolithic architectures to microservices
- real world system design case studies
- netflix distributed counter architecture
- airbnb soa migration monorail
- shopify modular monolith pod architecture
- high scale tech stacks comparison
- managing massive frontend monorepos
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 13 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Scaling Modern Systems: Architectural Evolutions and Real-World Tech Stacks

## TL;DR
Scaling modern software requires transitioning beyond monolithic designs through intentional decoupling, specialized storage layers, and workflow-specific optimization. While platforms like Airbnb and Netflix dismantled legacy monoliths into tiered services and gateway-routed microservices, Shopify demonstrates that modular monoliths running on isolated pods can achieve massive scale without distributed microservice overhead. Sustainable growth hinges on matching storage engines to workload patterns, offloading tasks asynchronously, and addressing developer tooling bottlenecks before repository scale stalls engineering velocity.

## Deconstructing the Monolith: Three Architectural Paths

When scaling engineering teams and consumer traffic, organizations generally follow one of three primary structural paths: Service-Oriented Architecture (SOA), distributed microservices, or a disciplined modular monolith.

```
Monolithic Origin
 ├── Airbnb  ─► 4-Tier Service-Oriented Architecture (SOA via Gateway)
 ├── Netflix ─► Orchestrated Microservices ─► Zuul Gateway Separation
 └── Shopify ─► Modular Monolith (Pods + MySQL + Kafka Isolation)
```

### 1. Airbnb: Tiered Service-Oriented Architecture
Airbnb originally operated as a monolithic Ruby on Rails application known internally as the "Monorail," which unified client presentation and server execution in a single deployment unit. Under hypergrowth serving over 1.5 billion guests and 4 million hosts across 200+ countries, this monolithic model faltered. Airbnb migrated away from the Monorail to a Service-Oriented Architecture governed by a gateway that distributes traffic across four discrete service strata:
- **Data Services:** The foundational layer providing isolated read and write access directly to data entities.
- **Derived Data Services:** Intermediate consumers that fetch data from underlying data services and apply lightweight business operations.
- **Middle Tier Services:** Core domain engines encapsulating complex business logic that spans multiple derived or baseline data entities.
- **Presentation Services:** Boundary-facing services that aggregate payloads across multiple backend layers and apply frontend-specific formatting before reaching clients.

### 2. Netflix: Progressive Microservice Decoupling
Netflix evolved its playback and streaming infrastructure across three distinct historical stages:
- **Stage 1 (Simple Monolith):** A traditional three-tier setup centered on the Netflix Content Control Protocol (NCCP), an all-inclusive monolithic application managing all capabilities.
- **Stage 2 (Orchestrated Microservices):** Feature capabilities were extracted into standalone applications to restore team velocity, yet the core orchestration remained bound to the monolithic NCCP application.
- **Stage 3 (Gateway Boundary):** Netflix isolated the critical playback path within NCCP while delegating all ancillary functionality to decoupled APIs, inserting the Zuul API Gateway at the edge to decouple clients from internal backend services.

### 3. Shopify: The Horizontally Partitioned Modular Monolith
Unlike companies that break architectures into discrete microservices, Shopify preserved a monolithic codebase built on Ruby on Rails, MySQL, Kafka, and Redis. By enforcing modular domain boundaries inside the application and segmenting deployment into isolated "pods" (autonomous runtime environments containing localized failure domains), Shopify scales to extreme thresholds. During peak events such as Black Friday 2024, this modular architecture processed 173 billion requests, sustained 284 million requests per minute, and served 12 terabytes per minute of edge traffic across more than 600,000 merchants.

## Architectural Evolution and Stack Comparison

| Organization | Core Foundation | Architecture Paradigm | Data & Storage Strategy | Key Scaling Technique |
| :--- | :--- | :--- | :--- | :--- |
| **Airbnb** | Ruby on Rails, API Gateway | 4-Tier Service-Oriented Architecture | Tiered Data and Derived Data Services | Complete elimination of the central monolith ("Monorail") into distinct service layers. |
| **Netflix** | Java ecosystem, Zuul Gateway | Edge-routed Microservices | Cassandra time-series buckets, EVCache, Rollup Queues | Decoupling the playback core from feature APIs; dedicated write rollup pipelines. |
| **Shopify** | Ruby on Rails, React, Kafka | Modular Monolith | MySQL, Redis, Memcached | Failure-domain isolation via pods; internal modular boundaries; custom deployment via ShipIt. |
| **Instagram** | Django / Express, Celery | Asynchronous Layered Microservices | PostgreSQL (relational), Cassandra (feeds), Redis, Object Storage | Strict separation between synchronous transactions and asynchronous queue workers. |

## Data Layer Specialization and High-Throughput Processing

As traffic increases, universal storage patterns degrade. Systems must partition data storage based on consistency requirements and query access profiles.

### Multi-Model Storage Distribution (Instagram Model)
To handle rich user engagements (likes, follows, uploads), Instagram isolates operational access into distinct storage systems:
- **Relational Databases (PostgreSQL):** Preserves structured data with strong consistency requirements, including account profiles, comments, and relationship graphs.
- **High-Write Data Stores (Cassandra):** Ingests high-volume, eventually consistent records such as user activity logs and feed updates.
- **In-Memory Caching (Redis / Memcached):** Fronts frequent reads to shield relational layers from repetitive queries.
- **Blob and Object Stores:** Houses raw image and video binaries, while references and metadata reside in transactional databases.
- **Asynchronous Task Queues:** Workloads such as notification delivery and relational fan-out bypass the HTTP request-response cycle entirely, routed through queues to background workers (like Celery).

### Rollup Aggregation: The Netflix Distributed Counter
Counting millions of events concurrently generates severe database row contention. Netflix solved this with a four-tier Distributed Counter Abstraction capable of servicing 75,000 requests per second at single-digit millisecond latency:
1. **Client API Layer:** Exposes basic primitives (`AddCount`, `GetCount`, `ClearCount`) via the Netflix Data Gateway.
2. **Event Logging & TimeSeries Storage:** Events receive a unique Event ID for idempotency and are written to Cassandra partitioned into immutable, time-scoped buckets to prevent write hotspots.
3. **Rollup Aggregation Pipeline:** Background rollup queues consume event batches, compute aggregates over fixed time windows, and store consolidated totals into a Cassandra Rollup Store.
4. **Read Optimization via Caching:** Aggregated counts are pushed to EVCache for high-speed retrieval, with background refresh workers updating stale cache records asynchronously.

## Developer Velocity and Repository Scaling

Architectural scaling challenges extend into internal developer workflows. As codebases expand, developer ergonomics degrade unless underlying tooling is actively re-engineered.

TikTok experienced this when its frontend TypeScript codebase grew into a monorepo containing over 200,000 files. At this scale, standard Git operations became unusable bottlenecks. To resolve this, TikTok developed **Sparo**, an optimization layer for Git operations in massive repositories:
- **Clone Duration:** Reduced from 40 minutes to 2 minutes.
- **Branch Checkout:** Reduced from 1.5 minutes to 30 seconds.
- **Working Tree Status (`git status`):** Reduced from 7 seconds to 1 second.
- **Commit Execution:** Reduced from 15 seconds to 11 seconds.

## Structural Layering and Network Fundamentals

Modern web applications consistently align with a nine-layer operational hierarchy across cloud platforms such as AWS:

```
[ Presentation (UI / Mobile / AirTag Mesh) ]
                    │
[ Edge Delivery (CDN / CloudFront / Caching) ]
                    │
[ Integration / Gateway (Zuul / API Gateway / AppSync) ]
         │                                │
[ Async Messaging (SQS/Kafka) ]   [ Business Logic (Fargate/ECS/Rails) ]
         │                                │
         └────────► [ Data Access Layer ] ◄┘
                          │
            [ Multi-Tier Data Storage ]
         (Aurora / Cassandra / S3 / Redis)
```

At the network transport boundary, these distributed layers rely on foundational protocols like the TCP three-way handshake:
1. **SYN:** The client initiates the connection by dispatching a SYN flag accompanied by an Initial Sequence Number (ISN).
2. **SYN-ACK:** The server acknowledges receipt by incrementing the client's ISN, setting the ACK and SYN flags, and providing its own ISN.
3. **ACK:** The client concludes negotiation by transmitting an ACK packet with the sequence number set to the server's incremented ISN, establishing an ordered, bidirectional communication stream.

## Common mistakes
- **Splitting into microservices by default:** Decomposing applications into microservices before team scale or domain boundaries require it introduces network overhead and orchestration complexity; Shopify proves a modular monolith can sustain 284 million requests per minute when properly isolated into pods.
- **Writing high-frequency counters directly to primary databases:** Attempting to update raw counters synchronously in a relational database creates row locks and contention; high-throughput counters require idempotent event bucketing, batch rollups, and cache fronting.
- **Overlooking source control performance:** Treating developer tooling as separate from systems architecture leads to severe productivity loss; repositories with hundreds of thousands of files require specialized tooling (such as TikTok's Sparo) to keep standard Git operations within interactive thresholds.
- **Using a single database engine for all data profiles:** Funneling low-latency transactional entities, high-throughput eventual write streams (feeds), and blob assets into a single relational database causes severe scalability bottlenecks; architectures must split workloads between relational tables, wide-column stores, object stores, and in-memory caches.

---
*Source: Summary in our own words of 13 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
