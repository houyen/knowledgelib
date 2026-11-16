---
id: software/system-design/bytebytego-archive-2025/concurrency-performance-memory
canonical_question: How do concurrency models, execution threads, and system performance metrics interact in software systems?
aliases:
- concurrency vs parallelism
- process vs thread differences
- java virtual threads vs platform threads
- latency vs throughput explained
- system performance metrics qps tps
- computer memory hierarchy levels
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 7 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Concurrency, Execution Models, and System Performance Metrics

## TL;DR
Concurrency structures software to manage multiple overlapping tasks, whereas parallelism executes computations simultaneously across multiple physical processor cores. Modern environments manage execution through isolated operating system processes, kernel threads, and lightweight user-space abstractions such as Java virtual threads that optimize blocking I/O. System capacity is bounded by the hardware memory hierarchy and evaluated using interdependent performance metrics: latency, throughput, queries per second, completed transactions, and active concurrency.

## Concurrency vs. Parallelism
Concurrency and parallelism describe fundamentally different aspects of computing systems. As Go co-creator Rob Pike observed, concurrency is about dealing with many things at once, whereas parallelism is about doing many things at once. Concurrency pertains to program structure and design, while parallelism pertains to physical hardware execution.

A concurrent application structures code into independently managed tasks whose execution lifetimes overlap in time without necessarily executing at the exact same physical instant. On a single-core CPU, the operating system achieves concurrency through rapid context switching, interleaving time slices across tasks to give the perception of simultaneous progress. Concurrency is ideal for handling idle waiting periods, such as waiting on network packets, database queries, file system access, or user input.

Parallelism requires multiple processing units or CPU cores. It divides compute workloads to execute multiple instructions at the exact same physical instant. Parallelism focuses strictly on increasing computational throughput for CPU-bound tasks, such as mathematical modeling, data analytics, image processing, and graphics rendering.

| Dimension | Concurrency | Parallelism |
| :--- | :--- | :--- |
| **Core Focus** | Program structure and task composition | Simultaneous physical instruction execution |
| **Hardware Need** | Single-core or multi-core processors | Strictly requires multiple processor cores |
| **Primary Mechanism** | Context switching and task interleaving | Simultaneous multi-core execution |
| **Ideal Workload** | I/O-bound and high-latency waiting | CPU-bound computation and heavy data processing |

## Execution Models: Processes, Threads, and Virtual Threads
Applications execute across three primary tiers of execution units, spanning operating system primitives to runtime-managed threads.

### Processes and Platform Threads
An operating system process is an independent execution context with its own isolated virtual memory space. Because processes do not share memory, spawning, destroying, and switching between them represents a heavyweight operation with noticeable CPU overhead.

Threads exist as subsets inside a host process and share its heap and allocated resources. This shared memory space makes inter-thread communication significantly faster than inter-process communication. However, traditional platform threads map 1:1 to underlying operating system kernel threads. Each platform thread consumes dedicated OS memory for its call stack, which limits the total number of concurrent platform threads a system can host before degrading or exhausting memory.

### Java Virtual Threads
To overcome the scaling limits of platform threads, Java introduced Virtual Threads (previewed in Java 19 and made stable in Java 21). Virtual threads do not replace platform threads and do not map 1:1 to operating system threads. Instead, they operate as lightweight, user-space threads managed directly by the Java Virtual Machine (JVM).

The JVM schedules virtual threads onto a small pool of underlying OS platform threads, known in this context as carrier threads. When a virtual thread executes a blocking operation—such as network I/O, database access, or sleep calls—the JVM unmounts it from its carrier thread without blocking the underlying OS thread. The carrier thread is immediately freed to execute other virtual threads. Once the blocking call completes, the JVM reschedules the virtual thread onto any available carrier thread. This design allows a system to support millions of concurrent, largely I/O-bound tasks without exhausting operating system thread pools.

| Execution Unit | Memory Space | Managed By | Relative Cost | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Process** | Isolated address space | OS Kernel | Heavyweight | Strict security and fault boundaries |
| **Platform Thread** | Shared within parent process | OS Kernel | Moderate | CPU-bound computation and legacy APIs |
| **Virtual Thread** | Shared within JVM | Language Runtime (JVM) | Extremely lightweight | Massive concurrent I/O operations |

## The Computer Memory Hierarchy
The execution speed of concurrent routines is directly constrained by the physical memory pyramid. As data moves from external sources toward the CPU, it travels through distinct layers balancing speed against storage volume:

1. **Input Sources:** Devices such as keyboards, mice, cameras, and network interfaces that inject data into the system.
2. **Permanent Storage:** Non-volatile storage mediums (hard drives, USB drives, ROM/BIOS, network storage) that hold system files, binaries, and persistent media.
3. **System RAM:** The volatile workspace of the computer, containing physical memory and virtual memory addressing to store running applications and active data.
4. **CPU Cache (Level 1 and Level 2):** High-speed SRAM located immediately next to or inside the CPU, speeding up access to frequently referenced instructions and memory addresses.
5. **CPU Registers:** The fastest and smallest memory units in the system, embedded inside the CPU to execute instructions instantaneously.

Moving higher up the memory pyramid delivers faster access speeds and lower latency at the expense of storage capacity and higher manufacturing costs.

## Performance Metrics: Latency, Throughput, and Saturation
Diagnosing performance bottlenecks requires quantifying system behavior through concrete operational metrics:

### Latency vs. Throughput
Latency measures the elapsed delay per request or packet. It represents the time required for a request to travel from the client, process on the server, and return. Latency includes server execution time, queuing delays, network propagation, transmission delays, and last-mile connectivity. It directly dictates user-perceived responsiveness.

Throughput measures aggregate capacity—the volume of data or requests successfully delivered within a given timeframe. While latency tracks individual packet speed, throughput reflects how many packets flow through the pipe without choking the system.

### Operational Metrics
Engineers evaluate system capacity using four foundational metrics:
- **Queries Per Second (QPS):** The rate of incoming requests received by a server each second. Systems often handle short bursts of peak QPS, but sustained high QPS risks service degradation if capacity is exceeded.
- **Transactions Per Second (TPS):** The rate of fully completed, end-to-end transactions processed per second, including database round-trips and finalized responses.
- **Concurrency:** The number of active, in-flight requests a system is processing at any single moment.
- **Response Time (RT):** The total elapsed time between request dispatch and response receipt, measured at both server and client levels.

These metrics relate through a governing formula:
$$\text{QPS} = \frac{\text{Concurrency}}{\text{Average Response Time}}$$

Under this relationship, increasing concurrency or reducing average response time directly yields higher system throughput.

| Metric | Definition | Core Signal | Optimization Target |
| :--- | :--- | :--- | :--- |
| **Latency / RT** | Delay per individual request | Responsiveness | Minimize to eliminate user delay |
| **Throughput** | Volume delivered per unit time | Channel capacity | Maximize to prevent queuing |
| **QPS** | Incoming requests received per second | Inbound request load | Balance against server capacity |
| **TPS** | Completed workflows per second | Business throughput | Maximize via backend efficiency |
| **Concurrency** | Simultaneous active requests | In-flight resource load | Support via pooling and async threads |

## Common mistakes
- **Conflating concurrency with parallelism:** Assuming that breaking a CPU-heavy task into concurrent routines accelerates execution on a single core, where context-switching overhead actually degrades performance.
- **Equating high bandwidth with low latency:** Assuming that a high-throughput network connection guarantees fast response times, overlooking queuing delays and network propagation lags that slow individual requests.
- **Confusing incoming request volume (QPS) with completed business units (TPS):** Evaluating server health based solely on received queries rather than fully completed database transactions.
- **Using virtual threads for CPU-bound computations:** Applying Java virtual threads to heavy computational tasks where thread unmounting does not occur, providing no throughput benefit over standard platform threads.
- **Sizing infrastructure for peak QPS without modeling response times:** Failing to account for how increased response times inflate concurrent in-flight requests, leading to thread exhaustion and connection pool depletion during sustained traffic spikes.

---
*Source: Summary in our own words of 7 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
