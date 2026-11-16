---
id: software/system-design/book-60-days/infrastructure-storage-security-and-saas
canonical_question: How do you select pragmatic system design architectures and avoid common over-engineering traps across storage, latency, security, ML serving, and application topology?
aliases:
- cloud system design trade-offs
- choosing s3 vs efs vs ebs
- cross region read replicas vs active active
- aws secrets manager vs hashicorp vault
- ml inference dynamic batching vs quantization
- modular monolith vs microservices greenfield
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 30, 31, 32, 50, 60 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Practical System Design: Architectural Pragmatism and Anti-Patterns

## TL;DR
Sound architectural design chooses the lowest-maintenance abstraction that satisfies current operational boundaries and deadlines. Default to managed, cloud-native services over self-operated clusters, read-path optimizations over distributed transaction engines, dynamic batching over premature model splitting, and disciplined modular monoliths over distributed microservices. Premature optimization introduces distributed systems overhead long before organizational scale justifies it.

---

## Scenario 1: Multi-Consumer File Storage (Day 30)
**Problem:** Selecting a unified storage layer on AWS for an upload service handling 10TB scaling to 100TB, consumed concurrently by an API, an ML pipeline, and an audit worker.

### Recommended Strategy: Amazon S3
Standard object storage (S3) acts as a decoupled, universally accessible storage repository where application databases store lightweight object keys rather than raw byte streams. 
- **Cost efficiency:** At 100TB, baseline object storage costs roughly $2,300 per month, with automated lifecycle rules routing inactive data to archive tiers (such as Glacier) at even lower costs.
- **Operational automation:** Built-in event hooks notify downstream consumers (such as the ML processing pipeline) as soon as an asset lands, eliminating custom pollers.
- **Built-in compliance:** Encryption at rest, versioning, access policies, and audit trails function out of the box with zero capacity provisioning.

### Failed Alternatives & Anti-Patterns
- **Elastic Block Store (EBS):** EBS volumes attach to a single compute instance at a time. The moment secondary workers or horizontal auto-scaling groups require access to the data, local block storage isolates files to whichever node handled the initial write.
- **Elastic File System (EFS):** EFS provides multi-instance POSIX shared filesystem access, but bills at approximately $0.30 per GB per month. At 100TB, monthly expenditure reaches roughly $30,000—a thirteen-fold cost increase over object storage without providing value to modern HTTP services consuming SDKs.
- **Self-Hosted MinIO on EC2:** While API-compatible with S3, running MinIO shifts disk monitoring, replication, node failovers, backup management, and off-hours outages onto your internal team. Below petabyte-scale egress boundaries, staff overhead rapidly eclipses managed cloud storage costs.

| Storage Option | Multi-Instance Access | Monthly Cost at 100TB | Operational Burden | Best Fit |
| :--- | :--- | :--- | :--- | :--- |
| **S3 (Selected)** | Global via HTTP API | ~$2,300 | Zero (Fully Managed) | Greenfield cloud microservices & decoupled consumers |
| **EBS** | Single instance only | ~$8,000–$10,000 | Low | Single-node relational databases & boot drives |
| **EFS** | Multi-instance POSIX | ~$30,000 | Low | Legacy software requiring direct filesystem syscalls |
| **Self-Hosted MinIO** | Global via HTTP API | Compute + Disk + Ops overhead | Very High | Multi-petabyte private data centers with dedicated SREs |

---

## Scenario 2: Cross-Region Latency on an Immovable Deadline (Day 31)
**Problem:** Sluggish 380ms average round-trip times impacting 30% of an e-commerce user base in Europe, with a 6-week delivery cutoff before Black Friday traffic surges.

### Recommended Strategy: Active-Passive Deployment with Read Replicas
Deploy an application replica alongside an Amazon RDS PostgreSQL cross-region read replica in `eu-west-1`, retaining `us-east-1` as the single primary writer.
- **Speed to delivery:** Provisioning a read replica requires minimal operational effort (typically one to two days) and demands no disruptive application rewrites.
- **Targeted relief:** E-commerce traffic is overwhelmingly read-dominated (product browsing, catalog queries, profile lookups). Local replicas drop read latencies from 380ms down to roughly 15ms.
- **Pragmatic trade-offs:** Replication lag generally settles under 100ms. Checkout mutations continue routing back to the US primary, preserving strict inventory consistency while providing a rapid disaster recovery failover target.

### Failed Alternatives & Anti-Patterns
- **Active-Active with Distributed Database (CockroachDB/Aurora Global):** Migrating relational engines under a six-week deadline invites severe execution risk. Resolving clock skew, distributed transactions, and unanticipated latency anomalies requires quarters of engineering validation.
- **CDN and Edge Caching Alone:** Edge networks accelerate static media and invariant GET endpoints, but cannot safely resolve authenticated, user-specific reads (shopping carts, localized order statuses) or database bottlenecks.
- **Active-Active with Eventual Consistency:** Dual-region asynchronous writes create distributed race conditions. A 200ms synchronization window allows different regions to sell identical physical stock, causing overselling and duplicate financial charges.

| Pattern | Read Latency | Implementation Time | Consistency Risk | Operational Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Read Replica (Active-Passive)** | ~15ms | 1–2 days | Minimal (<100ms replication delay) | Low |
| **Distributed Multi-Region DB** | Low | Months | Low (Consensus managed) | Extreme under tight deadlines |
| **CDN Only** | Variable | Hours | Low | High (Fails to resolve dynamic reads) |
| **Asynchronous Multi-Primary** | ~15ms | Weeks | Severe (Split-brain, stock overselling) | High |

---

## Scenario 3: Secrets Management and Audit Compliance (Day 32)
**Problem:** Remediating hardcoded passwords, unencrypted tokens, and absent credential lifecycles across production services under SOC 2 audit scrutiny without downtime.

### Recommended Strategy: AWS Secrets Manager
Centralize secrets into AWS Secrets Manager, accessing them at application startup or via runtime SDK clients governed by AWS IAM roles.
- **Audit conformity:** Secrets Manager natively registers every access event directly to AWS CloudTrail, furnishing the verifiable access logs necessary for SOC 2 auditors.
- **Automated rotation:** Offers turn-key credential rotation for RDS instances and programmable Lambda triggers for arbitrary API tokens.
- **Low-friction cutover:** Applications substitute environment reads with SDK client calls (`getSecretValue()`). At roughly $0.40 per secret per month, twenty credentials cost approximately $8 monthly with no infrastructure maintenance.

### Failed Alternatives & Anti-Patterns
- **HashiCorp Vault:** Vault provides robust ephemeral credentials, but requires managing high-availability Raft clusters, manual unsealing routines, and dedicated operational support. For an AWS-centric organization under 50 engineers, the operational footprint introduces significant availability risks.
- **CI/CD Injected Environment Variables:** Build pipelines are suitable for deploy-time tokens (e.g., container registry credentials), but fail runtime requirements. Static environment variables injected into tasks cannot be rotated atomically and lack runtime access auditing.
- **Custom KMS Encryption in an Application DB:** Building a homemade secrets repository reintroduces the fundamental bootstrapping dilemma: protecting the credentials that unlock the secrets database itself.

| Secret Solution | Runtime Audit Trail | Operational Overhead | Dynamic Rotation | Infrastructure Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **Secrets Manager (Selected)** | Native CloudTrail logs | Zero | Turn-key & Lambda hooks | Managed cloud service |
| **HashiCorp Vault** | Comprehensive audit logs | High (Clustering, unsealing) | Advanced dynamic leases | Dedicated server fleet |
| **CI/CD Injected Env Vars** | None at runtime | Low | Requires redeployment | CI runner configuration |
| **KMS + Custom DB** | Custom application logs | Medium | Manual development | Self-managed database tables |

---

## Scenario 4: High-Throughput ML Serving Starvation (Day 50)
**Problem:** A 6-billion parameter PyTorch model deployed on an 80GB A100 GPU encounters 4.2-second P99 latencies at 3,000 requests per second, despite the GPU sitting at only 23% utilization.

### Recommended Strategy: Dynamic Batching
Incorporate dynamic batching within the model serving layer (e.g., NVIDIA Triton, TorchServe, or vLLM) to group concurrent inputs within a tight latency window (e.g., 50ms) into single forward passes of 32 to 128 items.
- **Hardware alignment:** GPUs achieve computational saturation when parallelizing matrix operations across multiple tensor dimensions. Sequential single-request execution starves compute cores, expending more time on kernel launch overhead than actual floating-point calculations.
- **Utilization recovery:** Dynamic grouping elevates GPU saturation from 23% to 85–90%, dramatically multiplying overall system throughput and deflating tail request queues without adding compute instances.

### Failed Alternatives & Anti-Patterns
- **INT8 Quantization:** Precision reduction drops memory consumption and slightly speeds up computation (1.5x–2x), but the model already fits safely inside the 80GB VRAM. Compressing weights does not cure compute starvation caused by serialized execution.
- **Tensor Parallelism:** Sharding model weights across multiple GPUs addresses memory limits or extreme single-token latencies on massive parameter architectures. Applying it to a 6B parameter model that already fits onto a single A100 adds complex NVLink communication overhead and multiplies hosting costs.
- **Asynchronous Task Queues:** Queuing requests buffers incoming HTTP calls to eliminate gateway dropouts, but treats the symptom rather than the disease. Serial inference execution rates remain unchanged, leaving end-to-end user turnaround times unaddressed.

| Technique | Primary Purpose | Impact on GPU Utilization | Tail Latency Fix at 3k RPS | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Dynamic Batching** | Parallelize request evaluation | Major Increase (23% → 85%+) | Resolves queue bottleneck | Low (Framework native) |
| **Quantization (INT8)** | Reduce VRAM / memory bandwidth | Minor | Insufficient (Remains serialized) | Medium (Accuracy validation needed) |
| **Tensor Parallelism** | Split large models over cards | Neutral to Negative | Insufficient (Adds node sync) | High (Multi-GPU clustering) |
| **Task Queue Decoupling** | Absorb burst spikes | None | None (Hides execution delay) | Low to Medium |

---

## Scenario 5: Greenfield SaaS Platform Architecture (Day 60)
**Problem:** Constructing a multi-tenant SaaS application targeting 50,000 requests per second, incorporating real-time telemetry and AI interfaces, constrained by a strict 3-month launch window.

### Recommended Strategy: Modular Monolith
Structure the system as a unified deployable code artifact organized into strictly bounded, internally decoupled application modules (e.g., identity, billing, inference, core logic) with isolated data schemas.
- **High-velocity boundary discovery:** When starting from scratch, team assumptions about domain boundaries are frequently incorrect. Code-level refactoring inside a single repository is vastly cheaper than modifying network APIs and data models across decoupled services.
- **Scale mechanics:** Sustaining 50,000 requests per second is a standard horizontal stateless scaling pattern managed by load balancers, not an automatic justification for microservices.
- **Simplicity:** Eliminates inter-service network serialization, distributed transaction coordination, and complex telemetry overhead. Heavy AI inference remains shielded behind clean module interfaces to facilitate future extraction when isolated resource profiles warrant it.

### Failed Alternatives & Anti-Patterns
- **Microservices from Inception:** Launching with numerous decoupled services prior to understanding domain boundaries leads to distributed monoliths, cross-service transaction synchronization bugs, and excessive network latency.
- **Fully Serverless (Function-as-a-Service):** 50,000 sustained requests per second averaging 100ms equates to 5,000 concurrent Lambda executions. This volume yields severe cloud execution invoices compared to reserved compute, risks cold-start spikes on real-time routes, and hits execution time limits on AI inference workloads.
- **Event-Driven Kafka Core from Day One:** Mandating asynchronous event streams before validating product-market fit forces every feature to manage eventual consistency, schema registry governance, and asynchronous debugging hurdles during early development cycles.

| Architecture Style | Development Speed | Boundary Refactoring Cost | Operational Footprint | Viability at 50k Constant RPS |
| :--- | :--- | :--- | :--- | :--- |
| **Modular Monolith** | Maximum | Negligible (In-memory changes) | Minimal (Single deployable) | High (Scale compute horizontally) |
| **Microservices** | Low | Very High (Network APIs/schemas) | Very High (Multiple pipelines/repos) | High (Substantial infra overhead) |
| **Serverless (FaaS)** | High early, poor later | Medium | Low | Low (Costly & cold-start prone) |
| **Event-Driven / Kafka** | Low | High (Event schema migrations) | High (Cluster maintenance) | High (Excessive early complexity) |

---

## Decision cheatsheet

| Symptom / Constraint | Root Failure Mode | Recommended Pattern | Antipattern to Avoid |
| :--- | :--- | :--- | :--- |
| Multi-service file sharing at scale | Shared filesystem cost & concurrency | Object Storage (S3) | POSIX network shares (EFS) or instance disks (EBS) |
| Remote read latency under immovable deadline | Database migration delivery risk | Cross-Region Read Replica | Multi-primary active-active rewrites |
| Scattered keys facing audit review | Unaudited environment configurations | Cloud-Native Secret Store | In-house encryption engines or raw CI variables |
| High inference latency + Idle GPU compute | Serial kernel launch starvation | Dynamic Request Batching | Model quantization or task queueing |
| Greenfield app with high expected throughput | Premature boundary decomposition | Modular Monolith | Microservices or Event-Driven architectures from day one |

---
*Source: Summary in our own words of scenario days 30, 31, 32, 50, 60 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
