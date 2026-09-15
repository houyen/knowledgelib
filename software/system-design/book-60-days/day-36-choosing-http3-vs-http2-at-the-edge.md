---
id: software/system-design/book-60-days/day-36-choosing-http3-vs-http2-at-the-edge
canonical_question: Choosing HTTP3 vs HTTP2 at the Edge
aliases:
- System Design Day 36
- Choosing HTTP3 vs HTTP2 at the Edge
- Day 36 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 36: Choosing HTTP3 vs HTTP2 at the Edge

DAY 36 · SYSTEM DESIGN
Choosing HTTP/3 vs HTTP/2 at the Edge
Your API response went from 320ms to 95ms after a CDN switch.
Nothing changed on the server. Same origin. Same payload.
The only difference: the CDN started speaking HTTP/3 to your clients.
Here's the setup:
Mobile app →  Load Balancer →  Origin (NestJS) →  DB
Every request goes through the CDN first. Latency is acceptable — until high packet-loss environments
(mobile 4G →  5G transitions, flaky WiFi, Asia-Pacific routes). You're seeing 800ms+ tail latency for the
p99. The CDN supports HTTP/2 and HTTP/3. What do you enable?
A HTTP/2 only — multiplexing over a single TCP connection eliminates the old HTTP/1.1 head-of-
line problem. Proven, widely supported.
B HTTP/3 only — built on QUIC (UDP), eliminates TCP head-of-line blocking entirely, 0-RTT
connection resumption. Modern clients handle it fine.

---

DAY 36 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — HTTP/3 to clients, HTTP/2 to origin
The problem is the last mile. Mobile clients on lossy connections are where TCP falls apart.
HTTP/2 fixed HTTP/1.1's application-layer head-of-line blocking by multiplexing streams over one
TCP connection. But TCP itself still has head-of-line blocking at the transport layer. A single lost
packet stalls ALL streams until it's retransmitted. On a 4G connection dropping 2% of packets, your
20-stream HTTP/2 connection grinds to a halt.
HTTP/3 runs on QUIC (UDP). Each stream is independent. A dropped packet stalls only that stream,
the other 19 keep flowing. Add 0-RTT resumption (subsequent connections skip the handshake
entirely) and you shave 1-2 round trips on every reconnect. That's where the latency gains come from.
But your datacenter leg (CDN to origin) is a different story. It's a stable, low-loss private network.
QUIC's benefits disappear on reliable connections. HTTP/2 multiplexing is mature, well-optimized,
and doesn't carry QUIC's CPU overhead for cryptography (QUIC encrypts everything at the transport
layer, no cleartext, ever).
