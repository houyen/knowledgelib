---
id: software/system-design/bytebytego-archive-2025/http-url-dns-browser-request
canonical_question: What happens end-to-end when a user navigates to a URL in a web browser?
aliases:
- what happens when you type a url into a browser
- web navigation lifecycle from dns to rendering
- http evolution differences http 1 2 3
- real time web communication websocket vs sse vs polling
- browser rendering pipeline dom cssom layout paint
- dns lookup process root tld authoritative
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# The Web Navigation Lifecycle: From URL Input to Page Execution

## TL;DR
Entering a web address triggers a cascading sequence spanning client-side caching, hierarchical DNS resolution, network handshakes, protocol-level data transfer, and graphical rendering. The browser first resolves the host to an IP address across local and remote lookup tiers, then negotiates a secure transport layer (TCP and TLS or UDP-based QUIC). Once the web server responds to the HTTP request, the client engine transforms raw HTML, CSS, and JavaScript into an interactive, painted interface while managing real-time data flow through polling, SSE, or WebSockets.

## Anatomy of a Web Request: The URL
Before a network dispatch begins, the browser decomposes the entered Uniform Resource Locator (URL) into functional targets:
- **Scheme / Protocol:** Declares the communication rule set (e.g., `http`, `https`, `ftp`).
- **Domain and Port:** Identifies the remote host name and target network service endpoint.
- **Resource Path:** Pinpoints the hierarchical route to the requested asset on the host.
- **Query Parameters:** Key-value pairs prefixed by a question mark (`?`) and delimited by ampersands (`&`) to supply request parameters.
- **Fragment Identifier:** Marked by a hash (`#`) to direct the client to an internal page section or resource anchor without triggering a server retrieval.

## IP Resolution: The Multi-Tier DNS Lookup Chain
Because network routing operates on IP addresses rather than human-readable domain names, the browser must map the domain using the Domain Name System (DNS). The client initiates a lookup chain that stops at the earliest cache hit:

1. **Local Caching Layers:** The browser queries its own internal history, followed by the operating system DNS cache, and local networking equipment caches.
2. **Recursive DNS Resolver:** On a cache miss, the query forwards to a recursive resolver (typically operated by an Internet Service Provider or public provider such as Cloudflare or Google).
3. **Root Nameservers:** If the resolver lacks cached records, it asks root servers to identify the authoritative Top-Level Domain (TLD) servers for the target extension (such as `.com`).
4. **TLD Nameservers:** The TLD server directs the resolver to the authoritative nameservers responsible for the specific domain.
5. **Authoritative Nameservers:** These servers store the canonical `A` (IPv4) or `AAAA` (IPv6) records, returning the actual IP address (e.g., `172.67.21.11`). The resolver caches this record and passes it back to the client OS and browser.

## Connection Establishment and Transport Security
With the IP address resolved, the browser prepares the transmission channel. For traditional HTTPS:
1. **TCP Three-Way Handshake:** The client and server synchronize transport state by exchanging `SYN`, `SYN-ACK`, and `ACK` packets.
2. **TLS Handshake:** The server presents its digital certificate containing a public key. The client verifies the certificate, encrypts a generated symmetric session key with the server's public key, and transmits it. The server decrypts the session key with its private key, allowing subsequent communication to proceed over high-speed, symmetric encryption.

## Evolution of the HTTP Protocol
Application-layer exchange has undergone structural redesigns to eliminate network serialization bottlenecks:

| Version | Year | Transport Layer | Core Capabilities & Architectural Shifts |
| :--- | :--- | :--- | :--- |
| **HTTP/0.9** | 1991 | TCP | Raw document retrieval via single `GET` commands; no headers or status codes. |
| **HTTP/1.0** | 1996 | TCP | Introduced headers, HTTP status codes, and multi-format payloads; closed connection per request. |
| **HTTP/1.1** | 1997 | TCP | Added persistent connections (`Keep-Alive`), request pipelining, and granular caching headers. |
| **HTTP/2** | 2015 | TCP | Binary framing, full stream multiplexing over a single TCP connection, HPACK header compression, and server push. |
| **HTTP/3** | 2019 | UDP (via QUIC) | Replaces TCP with QUIC over UDP to eliminate head-of-line blocking on packet loss and provide zero-RTT reconnection. |

## Server Responses, Status Codes, and Real-Time Patterns
The server processes the incoming request and returns a structured response containing a three-digit status code:
- **1xx (Informational):** Request initiated; continuation in progress (e.g., `100 Continue`).
- **2xx (Success):** Operation received, verified, and completed (e.g., `200 OK`).
- **3xx (Redirection):** Action required to reach new target location (e.g., `301 Moved Permanently`).
- **4xx (Client Error):** Flawed syntax, invalid target, or missing authorization (e.g., `404 Not Found`).
- **5xx (Server Error):** Server encountered an unhandled exception or upstream timeout (e.g., `500 Internal Server Error`).

Because HTTP servers cannot natively open spontaneous TCP connections to clients, applications adopt specific bidirectional communication patterns:

| Pattern | Initiator | Duplex Mode | Connection Model | Overhead / Trade-off |
| :--- | :--- | :--- | :--- | :--- |
| **Short Polling** | Client | Half-duplex | Sequential discrete HTTP requests on fixed timers | High network and CPU overhead from repeated empty responses. |
| **Long Polling** | Client | Half-duplex | Client opens HTTP request; server hangs until data arrives | Reduces empty hits; still incurs full HTTP header retransmission per cycle. |
| **Server-Sent Events (SSE)** | Server (after setup) | Simplex (unidirectional) | Long-lived persistent HTTP connection streaming text | Minimal overhead for server-to-client feeds; cannot send client commands over same pipe. |
| **WebSockets** | Both | Full-duplex | HTTP connection upgraded to persistent, bidirectional framing | Lowest latency for interactive messaging; requires managing separate stateful sockets. |

## Browser Parsing and the Rendering Pipeline
Upon reading the HTTP payload (HTML, CSS, JavaScript), the browser layout engine constructs the view:
1. **Document Parsing:** The tokenizer parses HTML characters into nodes to construct the Document Object Model (DOM). In parallel, style rules are parsed into the CSS Object Model (CSSOM).
2. **Render Tree Generation:** Combining the DOM and CSSOM creates a Render Tree, filtering out invisible elements (such as `<head>` or nodes styled with `display: none`).
3. **Layout / Reflow:** The engine calculates exact geometric dimensions and coordinates for each visible node relative to the viewport.
4. **Painting and Compositing:** Pixels are drawn into layers (rasterization) and composited onto the screen via the GPU. JavaScript runs concurrently, altering DOM/CSSOM structures and triggering style recalibrations or repaints.

To accelerate this critical path, modern frontends apply optimization strategies:
- **Data Reduction:** Applying Brotli/Gzip compression, tree shaking (dead code elimination), and aggressive image optimization.
- **Delivery Scheduling:** Implementing code splitting, dynamic runtime imports, and windowing/virtual lists for large collections.
- **Speculative Fetching:** Utilizing resource hints (`pre-load`, `pre-fetch`) and prioritising above-the-fold assets over non-critical background scripts.

## Common Mistakes and Trade-offs
- **Choosing WebSockets when SSE suffices:** Deploying complex stateful WebSocket infrastructures for applications that only require unidirectional updates (such as ticker feeds or build logs) introduces unnecessary architectural complexity.
- **Neglecting TCP connection limits in HTTP/1.1:** Emitting dozens of simultaneous network calls under HTTP/1.1 runs into browser per-domain socket limits (usually 6), creating request queues; HTTP/2 multiplexing solves this over a single socket.
- **Uncontrolled long polling reconnections:** Reconnecting immediately upon every long-polling response without exponential backoff or jitter can trigger thundering-herd outages on upstream application servers during load spikes.
- **Over-bundling non-critical routes:** Delivering entire application codebases in an initial JavaScript bundle stalls parsing and compilation, degrading initial render times compared to split bundles loaded dynamically.

---
*Source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
