---
id: software/system-design/bytebytego-archive-2025/sql-relational-databases-indexing
canonical_question: How do relational databases process queries, organize storage, and optimize performance?
aliases:
- relational database internals guide
- sql query execution lifecycle
- database index types and data structures
- postgresql architecture and processes
- database normalization forms comparison
- database performance optimization strategies
- storage saving probabilistic data structures
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 9 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Relational Database Internals: Query Processing, Storage Architecture, and Performance Optimization

## TL;DR
Relational databases execute queries through a structured pipeline that spans network transport, SQL parsing, cost-based optimization, execution scheduling, and low-level storage engine coordination. Query throughput depends heavily on physical access paths—including clustered B+ trees, hash indexes, and bitmap structures—complemented by probabilistic algorithms that conserve memory. Scalability requires balancing write-safety normalization rules against read-focused denormalization, selecting appropriate concurrency controls, and partitioning workloads across physical boundaries.

## The Query Execution Pipeline
Executing a SQL statement requires coordination across four primary database subsystems:

1. **Transport Subsystem**: Manages client connection lifecycles, verifies user authentication, checks table-level permissions, and forwards authorized query strings to the query engine.
2. **Query Processor**:
   - *Query Parser*: Deconstructs the query text into syntactic elements (`SELECT`, `FROM`, `WHERE`), validates grammar, and compiles an abstract parse tree or relational algebra expression.
   - *Query Optimizer*: Evaluates the parse tree for semantic validity (e.g., verifying that referenced relations exist), inspects available index statistics, and generates a minimal-cost physical execution plan.
3. **Execution Engine**: Interprets the execution plan steps, coordinates intermediate result streams, directs operations down to the storage subsystem, and aggregates the final records returned to the client.
4. **Storage Engine Subsystems**:
   - *Transaction Manager*: Controls transaction lifecycles and preserves ACID properties.
   - *Lock Manager*: Allocates shared and exclusive locks to enforce concurrency constraints.
   - *Buffer Manager*: Regulates page transfers between disk storage and system memory cache.
   - *Recovery Manager*: Processes write-ahead logs to perform rollbacks and crash recovery.

## Process and Memory Architecture: The PostgreSQL Model
PostgreSQL illustrates how a dedicated multiprocess architecture isolates client workloads while sharing memory:

- **Process Model**: Written in C, the system relies on `Postmaster` as the supervisor process. It listens for client requests and spawns a dedicated server process for every active connection. Dedicated background workers are provisioned on demand for parallel operations.
- **Shared Memory Allocations**: A centralized shared memory segment enables cross-process communication. It contains Shared Buffers (cached table pages), WAL Buffers (in-memory write-ahead logs), `Clog` Buffers (commit status records), and Temporary Buffers.
- **Auxiliary Processes**:
  - *BG Writer & Checkpointer*: Flush modified memory buffers to disk to maintain consistency and reduce recovery overhead.
  - *WAL Writer*: Persists transaction logs to physical WAL storage.
  - *Auto Vacuum*: Cleans outdated dead tuple versions to avoid storage bloat.
  - *Stats Collector*: Gathers table access metrics to inform the optimizer.
  - *Archiver, System Logger, & Replication Launcher*: Handle point-in-time recovery logs, system error logs, and replica nodes.
- **Physical File Tiers**: Physical storage separates table data files, write-ahead log (`WAL`) files, archive backup sets, and operational diagnostic logs.

## Schema Normalization and Dependency Management
Relational modeling uses progressive normal forms to eliminate data anomalies and unnecessary duplication:

| Normal Form | Core Structural Rule | Anomaly / Redundancy Prevented |
| :--- | :--- | :--- |
| **1NF** | Enforces atomic column values; eliminates repeating attribute groups. | Multi-valued elements nested in single fields. |
| **2NF** | Satisfies 1NF; non-prime attributes must depend on the entire candidate key. | Partial functional key dependencies. |
| **3NF** | Satisfies 2NF; non-prime attributes must depend only on primary keys. | Transitive dependencies between non-key fields. |
| **BCNF** | Strengthens 3NF; every determinant attribute must be a candidate key. | Overlapping composite candidate key anomalies. |
| **4NF** | Satisfies BCNF; prohibits multiple independent multi-valued dependencies. | Redundant row multiplication across distinct 1-to-many relations. |

While normalization guarantees write integrity, it incurs performance costs through multi-table joins. Strategic denormalization collapses related tables into unified structures, trading extra storage and write overhead for faster read access.

## Physical Indexing and Core Data Structures
Indexes are auxiliary lookup structures mapping logical values to physical tuple addresses:

- **Primary Index**: Automatically bound to a table's primary key; can be dense (an entry per record) or sparse (entries pointing to data page boundaries).
- **Clustered Index**: Sets the physical ordering of data pages on disk. Tables are limited to one clustered index, which provides optimal I/O efficiency for range scans.
- **Secondary Index**: An unclustered, auxiliary structure containing selected attribute values paired with pointers back to the base table or primary key.

| Index Structure | Node & Data Architecture | Optimal Workload | Limitations / Fit |
| :--- | :--- | :--- | :--- |
| **B-Tree** | Balanced tree; stores keys and record pointers across both internal and leaf nodes. | Point lookups and small range queries. | Branch traversal required across all levels. |
| **B+ Tree** | Internal nodes hold routing keys only; all record pointers sit in linked leaf nodes. | Sequential scans and wide range searches. | Deeper leaf lookups for point reads. |
| **Hash Index** | Computes a hash function over keys to locate bucket arrays containing pointers. | Exact equality comparisons (`=`). | Incapable of range queries or sorting. |
| **Bitmap Index** | Maintains bit vectors representing values across record identifiers. | Complex boolean predicates (`AND`, `OR`). | Limited strictly to low-cardinality attributes. |
| **Inverted Index**| Maps individual tokens and terms to arrays of matching row identifiers. | Full-text keyword searches. | High maintenance overhead during writes. |

## Space-Efficient Auxiliary Data Structures
High-scale databases leverage probabilistic or compressed structures to minimize resource footprints:

- **Bloom Filter**: Uses hashing across a bit vector to test set membership; guarantees zero false negatives with minimal memory, but does not support deletions.
- **Cuckoo Filter**: A compact alternative to Bloom filters that supports item deletion and faster lookup performance.
- **HyperLogLog**: Approximates distinct value counts (cardinality) across immense datasets within bounded, minimal memory.
- **Count-Min Sketch**: Tracks probabilistic frequency estimations for stream data within sublinear space.
- **Minhash**: Evaluates Jaccard similarity across large collections using compressed hash signatures.
- **SkipList**: A layered linked list implementing probabilistic hierarchy to achieve logarithmic search, insert, and delete times.

## Join Types and Concurrency Controls
- **Relational Joins**: `INNER JOIN` restricts output to matching rows across joined tables; `LEFT JOIN` and `RIGHT JOIN` retain all records from the base table while substituting NULL for unmatched target attributes; `FULL OUTER JOIN` preserves all rows from both tables, filling missing pairings with NULL.
- **Horizontal Scaling & Partitioning**: Sharding partitions data subsets across separate server instances to spread storage and query demands horizontally.
- **Replication**: Routes write operations to a primary instance while distributing read loads across read-only secondary replicas.
- **Locking Paradigms**: Systems control resource contention using pessimistic locks (blocking conflicting concurrent updates in advance) or optimistic locks (validating record version changes at commit time).

## Common Mistakes
- **Using Hash Indexes for Range Queries**: Query optimizers cannot perform range scans (`BETWEEN`, `<`, `>`) on hash indexes because hash calculations destroy sequential ordering; B+ trees must be used instead.
- **Attempting Multiple Clustered Indexes per Table**: A table's physical records can only be sorted in a single order on disk; all secondary search paths must use unclustered indexes.
- **Assigning Bitmap Indexes to High-Cardinality Fields**: Generating bit vectors on columns with thousands of distinct values (e.g., UUIDs or timestamps) creates excessive storage bloat; bitmaps should remain restricted to low-cardinality fields.
- **Relying on Standard Bloom Filters When Records Are Deleted**: Deleting items from standard Bloom filters causes false negatives by clearing shared bits; workloads requiring deletions must employ Cuckoo filters.
- **Over-Normalizing Read-Heavy Tables**: Strict 3NF or BCNF normalization on write-infrequent, high-throughput analytical schemas leads to severe join latency; these tables benefit from strategic denormalization.

---
*Source: Summary in our own words of 9 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
