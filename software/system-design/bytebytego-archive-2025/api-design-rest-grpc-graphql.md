---
id: software/system-design/bytebytego-archive-2025/api-design-rest-grpc-graphql
canonical_question: What are the fundamental principles, paradigms, and best practices for designing and implementing modern APIs?
aliases:
- api design best practices
- rest vs graphql vs grpc
- rest architectural constraints
- api pagination and idempotency
- api vs sdk differences
- how modern apis work
- api architecture fundamentals
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Modern API Architecture: Paradigms, Design Principles, and Best Practices

## TL;DR
Designing scalable APIs requires selecting the right paradigm—REST for predictable resource management, GraphQL for client-defined data aggregation, or gRPC for low-latency inter-service communication. Robust implementations depend on clear resource modeling using nouns, stateless interactions, explicit idempotency handling, and bounded pagination. Maintaining system reliability further requires enforcing end-to-end transport encryption, token verification, rate limiting, and disciplined versioning.

## API Communication Paradigms

APIs structure communication between software components across several architectural styles. Selecting a paradigm depends on performance constraints, network environment, and data consumption patterns.

| Dimension | REST | GraphQL | gRPC |
| :--- | :--- | :--- | :--- |
| **Primary Protocol** | HTTP/1.1 or HTTP/2 | Typically HTTP/1.1 or HTTP/2 | HTTP/2 |
| **Data Format** | JSON, XML, or plain text | JSON (via structured query text) | Protocol Buffers (Binary) |
| **Endpoint Model** | Multiple resource-oriented URLs | Single generalized endpoint | Procedural method stubs |
| **Network Efficiency** | Moderate; risks over- or under-fetching | High payload efficiency; single round-trip queries | Very high; binary encoding yields ~5x faster throughput than JSON |
| **Caching Complexity**| Simple; leverages standard HTTP headers | Complex; POST-heavy requests bypass native HTTP caches | Complex; relies on application-level caching |
| **Primary Use Case** | Public APIs, web integrations, uniform CRUD | Complex frontends with changing data shapes | Low-latency internal microservice communication |

### How gRPC Operates Under the Hood
Remote Procedure Call (RPC) frameworks allow a client to invoke remote service logic as if it were a local function call. 

In a typical microservice interaction (such as an order service contacting a payment service):
1. An incoming client request enters an edge service.
2. The service's gRPC client stub takes the payload, serializes it into a compact binary format, and passes it to the transport layer.
3. The binary payload travels across the network over HTTP/2, benefiting from header compression and connection multiplexing.
4. The destination server receives the packet stream, decodes the binary stub, and executes the target service application logic.
5. The return value undergoes binary serialization, travels back across the HTTP/2 connection, and is deserialized by the calling service to return to the caller.

## APIs Versus SDKs

While both bridge components in software systems, they fulfill separate roles:

* **Application Programming Interface (API):** A formal specification of communication rules, network endpoints, request formats, and response payloads that allows independent systems to exchange data across network boundaries.
* **Software Development Kit (SDK):** An ecosystem-specific suite of tools, libraries, documentation, and pre-built code samples. An SDK wraps lower-level API calls into high-level language abstractions tailored to a target language or runtime (such as mobile platforms or developer tools for third-party services like Stripe or Google Maps).

## The Six Architectural Constraints of REST

To qualify as a RESTful architecture, an API must adhere to six core constraints:

1. **Client-Server Architecture:** Decouples user interface concerns from data storage and core business processing, allowing client frontends and backend data stores to iterate independently.
2. **Statelessness:** Every inbound request must contain all necessary context, credentials, and parameters needed to execute it. The server never maintains client session state between calls.
3. **Uniform Interface:** Resources must follow consistent URIs and predictable formats across the entire system, standardizing interaction patterns regardless of underlying storage models.
4. **Cacheability:** Responses must explicitly declare whether they can be cached (using mechanisms like `Cache-Control` headers) to minimize unnecessary roundtrips and improve throughput.
5. **Layered System:** The architecture allows intermediate proxies, load balancers, caching servers, and security gateways between the client and application server without requiring client-side configuration changes.
6. **Code on Demand (Optional):** Servers may temporarily extend client capabilities by transmitting executable code (such as JavaScript) directly to the consumer.

## Essential API Design Standards

### Resource-Centric URI Modeling
URIs must represent entities using nouns rather than action verbs. Action logic is dictated by the HTTP method, not the path.
* **Correct:** `GET /products`, `POST /products`, `DELETE /products/{id}`
* **Incorrect:** `GET /api/getProducts`, `POST /api/deleteProduct`

Entity relationships should be expressed hierarchically in the path to preserve relational context (for example, `/users/{id}/orders`).

### HTTP Methods and Idempotency
An operation is idempotent if executing it multiple times produces the identical server state as executing it once.

* **Idempotent by Specification:** `GET`, `HEAD`, `PUT`, and `DELETE`.
* **Non-Idempotent:** `POST` (creates new resources on successive calls) and `PATCH` (modifies state incrementally unless restricted).

To make non-idempotent endpoints like `POST` safe against network retries, clients must provide a unique **Idempotency Key** in request headers. The server records this key in a low-latency datastore (such as Redis) alongside the resulting response. When a duplicate key arrives during a retry, the server returns the cached response rather than processing the transaction a second time.

### Collection Pagination
Unbounded queries exhaust server memory and congest network bandwidth. Datasets must be paginated using one of three strategies:

* **Offset-Based:** Uses parameters such as `?offset=20&limit=10`. Straightforward to implement, but suffers from performance degradation at high offsets and skips/duplicates records when underlying data changes.
* **Cursor-Based:** Passes an opaque token pointing to a specific record boundary. Stable under concurrent writes and optimal for continuous feeds.
* **Keyset-Based:** Uses natural ordered indexes (such as `WHERE id > last_seen_id LIMIT 10`) to provide high-performance database access without offset overhead.

### Query Filtering and Sorting
Use URL query parameters to support search criteria without introducing specialized endpoints. Applying clear key-value filters (for example, `?status=active&sort=created_at:desc`) keeps endpoint surfaces minimal and predictable.

### Authentication, Gateways, and Resilience
* **Transport and Identity:** HTTPS is mandatory across all environments. Identity is managed through mechanisms like API keys, Basic Auth, OAuth2, and Bearer JSON Web Tokens (JWTs). JWTs validate identity on every incoming request through three cryptographically bound components: header, payload, and signature.
* **Traffic Control:** Rate limiting must be enforced at the perimeter to prevent resource exhaustion and ensure high availability.
* **Edge Infrastructure:** API Gateways (such as Kong, Nginx, AWS API Gateway, Azure API Services, or Apigee) centralize load balancing, rate limiting, and authentication upstream from implementation frameworks like Node.js, Spring, FastAPI, Django, or Flask.
* **Contract Durability:** Endpoints require explicit versioning paths to update schemas without breaking existing client integrations.
* **Documentation & Testing:** Contracts should be maintained with documentation frameworks (such as OpenAPI/Swagger, Redoc, Postman, or DapperDox) and verified using tools like cURL, Postman, or SoapUI.

## Common Mistakes

* **Embedding Verbs in Resource Paths:** Exposing endpoints like `/api/createOrder` or `/api/getUser` instead of relying on standard HTTP methods (`POST /orders`, `GET /users`) violates uniform interface constraints.
* **Retrying Non-Idempotent Requests Without Deduplication:** Retrying raw `POST` operations after network timeouts without idempotency keys risks creating duplicate transactions, double charges, or corrupt system state.
* **Omitting Mandatory Pagination on Collections:** Returning unpaginated entity lists can crash application instances, exhaust database memory, and cause extreme payload bloat as collections scale.
* **Exposing GraphQL Without Query Safeguards:** Allowing arbitrary nested client queries without depth limits, pagination caps, or complexity analysis allows clients to trigger abusive, resource-draining database queries.
* **Modifying Live Endpoints Without Versioning:** Altering response payload formats or input validation requirements on existing routes without versioning breaks backward compatibility for active API consumers.

---
*Source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
