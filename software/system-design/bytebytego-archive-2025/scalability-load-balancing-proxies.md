---
id: software/system-design/bytebytego-archive-2025/scalability-load-balancing-proxies
canonical_question: How do traffic routing components, scalability strategies, and distributed algorithms fit together in system design?
aliases:
- system design architectural building blocks
- load balancer vs api gateway vs reverse proxy
- forward proxy vs reverse proxy differences
- system design interview algorithms
- architectural scalability bottlenecks and solutions
- traffic routing and edge server architecture
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 13 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Architecture, Traffic Routing, and Scalability in System Design

## TL;DR
Scalable architecture relies on removing centralized bottlenecks through stateless tiers, loose coupling, and asynchronous processing. Inbound traffic moves through a tiered ingress pipeline—from edge load balancers to API gateways for policy enforcement and reverse proxies for backend distribution. Distributed algorithms such as consistent hashing, Raft, leaky buckets, and Bloom filters provide the algorithmic foundation for consistent data placement, consensus, rate limiting, and memory efficiency across nodes.

## Scalability Foundations and Non-Functional Requirements

Scalability is not merely the technical capacity to process larger workloads, but the ability to do so through the repeated application of a cost-effective strategy. A system that cannot scale economically hits a functional limit regardless of its design.

System scalability is restricted by three primary bottlenecks:
1. **Centralized components:** Central control nodes or single datastores create single points of failure and throughput ceilings.
2. **High-latency operations:** Long-running, blocking operations deplete upstream resources and degrade responsiveness.
3. **Tight coupling:** Interdependent components prevent individual services from scaling horizontally based on demand.

To mitigate these bottlenecks, systems adhere to core design principles: maintaining stateless application layers, decoupling components through clear boundaries, and shifting heavy or deferred tasks to asynchronous, event-driven pipelines.

Architectural techniques address specific non-functional requirements (NFRs):

- **Availability:** Load balancers eliminate single points of failure by spreading incoming traffic across resilient server instances.
- **Latency:** Content Delivery Networks (CDNs) cache responses at edge servers geographically close to users.
- **Scalability:** Horizontal database sharding splits datasets into manageable subsets, while data replication distributes reads across multiple nodes.
- **Durability:** Write-ahead transaction logs capture state transitions sequentially, allowing complete data reconstruction during system recovery.
- **Consistency:** Eventual consistency models accept temporary divergence between replicas to maintain throughput, guaranteeing convergence over time.
- **Modularity:** High cohesion within components and loose coupling across service boundaries preserve maintainability.
- **Configurability:** Configuration-as-Code stores infrastructure definitions and runtime flags in versioned repositories without code modifications.
- **Resilience:** Asynchronous message queues isolate slow services, smooth traffic spikes, and buffer work for retry routines.

## Traffic Routing and Server Infrastructure

Modern architectures organize ingress infrastructure into coordinated layers. When a client issues a request, it traverses a structured sequence:

```
[ Client ]
    │
    ▼
[ Edge Load Balancer ]
    │
    ▼
[ API Gateway ] ── (Identity Provider / Auth)
    │           ── (Rate Limiting & Whitelisting)
    │           ── (Path Routing & Circuit Breaking)
    ▼
[ Reverse Proxy ] (SSL Termination, DDoS Defense)
    │
    ▼
[ Service-Layer Load Balancer ]
    │
    ▼
[ Microservice Instances ]
```

1. **Edge Load Balancing:** The client establishes an initial connection to an edge load balancer, which acts as the network entry point and fans out traffic to the gateway layer.
2. **API Gateway Inspection:** The gateway parses and validates HTTP attributes, evaluates allow/deny lists, and invokes external identity providers for authentication and authorization.
3. **Policy Enforcement and Routing:** Rate-limiting rules (such as leaky bucket algorithms) drop or delay requests that exceed configured quotas. If healthy, requests match routing paths, undergo protocol translation, and pass downstream.
4. **Resilience and Telemetry:** Gateways encapsulate circuit breakers to prevent systemic degradation when backends stall, utilize caching for read-heavy payloads, and ship telemetry into central logging engines like the ELK stack (Elasticsearch, Logstash, Kibana).
5. **Reverse Proxying and Service Dispatch:** Reverse proxies terminate SSL/TLS encryption, absorb DDoS attacks, and forward traffic to an internal service-layer load balancer, which delivers the payload to an individual worker instance.

### Ingress Server Roles

| Server / Component | Primary Orientation | Core Responsibilities | Typical Placement |
| :--- | :--- | :--- | :--- |
| **Forward Proxy** | Client-facing | Hides client identities, enforces organizational outbound browsing restrictions, and caches external content. | Client network edge |
| **Reverse Proxy** | Server-facing | Hides backend topology, terminates SSL/TLS, buffers slow clients, defends against DDoS, and caches upstream responses (e.g., Nginx). | Ingress / Pre-service tier |
| **Load Balancer** | Traffic distribution | Distributes network or application traffic across pools of servers to maximize availability and throughput. | Edge and internal service boundaries |
| **API Gateway** | Application-level routing | Centralizes authentication, authorization, schema validation, rate limiting, protocol translation, and circuit breaking. | Boundary between public clients and private services |
| **Origin Server** | Central content authority | Serves as the authoritative source of truth for assets that are cached and delivered downstream by CDNs and proxies. | Core backend storage |
| **Web Server** | Web asset delivery | Processes HTTP requests to deliver static or dynamic web files directly to consumers. | Application tier |

## Distributed Algorithms in Architecture

Distributed environments require specialized data structures and algorithms to coordinate state, manage storage, and govern traffic without central synchronization locks:

### Data Partitioning and Membership
- **Consistent Hashing:** Maps keys and nodes to a circular hash space, minimizing data migration when cluster nodes are added or removed.
- **Bloom Filters:** Fast, probabilistic bit arrays that verify whether an item is definitely absent from cache, preventing unnecessary disk read operations.

### Counting and Cardinality
- **HyperLogLog:** Memory-efficient probabilistic cardinality estimation used to count large volumes of unique user search queries.
- **Lossy Count:** Online frequency analysis algorithm used to identify heavy hitters and dominant trends across streaming network traffic.

### Replication and Consensus
- **Raft:** A leader-based consensus algorithm that maintains replicated write-ahead state machine logs across distributed server quorums.
- **Merkle Trees:** Binary hash trees that allow nodes to detect discrepancies across distributed data replicas by comparing cryptographic hashes of data partitions.
- **Rsync:** Algorithmic file synchronization that transmits only modified byte blocks across systems rather than copying full files.

### Geospatial and Traffic Shaping
- **Geohash and QuadTrees:** Spatial partitioning structures that index two-dimensional geographic coordinates for location-based querying.
- **Ray Casting:** Vector collision detection used to determine whether coordinates fall inside geographical boundaries.
- **Leaky Bucket:** Traffic-shaping rate limiter that buffers bursts and releases requests at a steady rate to prevent service exhaustion.

## Common Mistakes

- **Treating scalability as a pure infrastructure upgrade:** Adding hardware to monolithic systems with tightly coupled, high-latency components causes costs to surge without solving throughput limits; scaling strategies must be economically repeatable.
- **Conflating forward and reverse proxies:** Deploying a forward proxy internally fails to protect server topologies or terminate SSL, as forward proxies represent clients rather than backend targets.
- **Distributing cross-cutting governance into individual microservices:** Implementing authentication, IP filtering, and rate limiting within each microservice leads to configuration drift; these edge concerns belong in the API gateway.
- **Imposing strict consistency across replicated datastores:** Demanding absolute real-time consistency across distributed nodes degrades availability and increases latency; eventual consistency provides resilience during network splits.
- **Overlooking single points of failure in centralized coordinating components:** Placing load balancers in front of a system that relies on a single un-sharded, un-replicated database only relocates the bottleneck further down the stack.

---
*Source: Summary in our own words of 13 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
