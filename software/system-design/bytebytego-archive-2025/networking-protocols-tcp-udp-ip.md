---
id: software/system-design/bytebytego-archive-2025/networking-protocols-tcp-udp-ip
canonical_question: How do core networking hardware, transport protocols, standard ports, and diagnostic tools function together in modern network architectures?
aliases:
- networking fundamentals cheat sheet
- tcp vs udp protocols comparison
- hub vs switch vs router vs modem
- common network ports and services
- network troubleshooting commands guide
- transport and application protocol dependencies
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 12 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Modern Networking Architecture: Hardware, Protocols, Ports, and Diagnostics

## TL;DR
Computer networks rely on physical and virtual appliances to segment traffic, transport protocols to govern data transmission, and standard port conventions to route service traffic. Modems, routers, switches, and hubs operate at distinct layers of network isolation, while transport choices balance strict reliability (TCP) against raw speed (UDP) or multiplexed efficiency (QUIC). Maintaining and diagnosing these distributed systems requires understanding protocol dependencies and leveraging specific command-line utilities to inspect routing, sockets, and packets.

## Network Hardware and Traffic Segmentation
Network devices route data across boundaries by operating at distinct layers of the networking stack. Confusing their boundaries often results in suboptimal topologies, broadcast storms, or incorrect troubleshooting assumptions.

| Device | Primary Layer | Addressing Used | Scope & Isolation |
| :--- | :--- | :--- | :--- |
| **Modem** | Physical / Data Link | Carrier signals (coax, fiber, cellular) | Converts ISP analog/optical signals into digital frames; supplies a single public IP. |
| **Hub** | Layer 1 (Physical) | None (repeats raw electrical/optical bits) | Shares a single collision domain across all ports; broadcasts incoming traffic to all links. |
| **Switch** | Layer 2 (Data Link) | MAC addresses | Separates collision domains per port; forwards frames strictly to destination hardware within a LAN. |
| **Router** | Layer 3 (Network) | IP addresses | Separates broadcast domains; bridges disparate networks (e.g., LAN to WAN) via Network Address Translation (NAT). |

In consumer and small-office environments, modems and routers frequently merge into a single physical chassis. Functionally, the modem provisions the external link while the internal router operates a DHCP server to issue local addresses (such as `192.168.1.x`) and translates packets via NAT across the single public interface.

## Transport Protocols: TCP, UDP, and QUIC
Data movement over IP requires transport mechanisms tailored to application needs. TCP ensures absolute delivery at the cost of latency, UDP delivers minimal-overhead packets without sequencing guarantees, and QUIC combines aspects of both over UDP.

| Dimension | TCP | UDP | HTTP/3 (QUIC) |
| :--- | :--- | :--- | :--- |
| **Connection State** | Connection-oriented (3-way handshake: SYN, SYN-ACK, ACK) | Connectionless (fire-and-forget datagrams) | Connection-oriented over UDP abstraction |
| **Delivery Guarantees** | Ordered, retransmitted, duplicate-free | No delivery, arrival order, or duplicate protection | Ordered and reliable per stream |
| **Flow & Congestion Control** | Built-in windowing and congestion backoff | None | Integrated congestion control with stream isolation |
| **Security Mechanism** | Layered via TLS over TCP (e.g., HTTPS, LDAPS) | Optional application-level security (e.g., IPsec/DTLS) | Mandatory built-in TLS 1.3 |
| **Typical Protocols** | HTTP/1.1–2, SSH, SMTP, BGP, RDP, MySQL, Postgres | DNS queries, DHCP, NTP, SIP, RTP streaming | HTTP/3 web traffic, modern mobile APIs |

QUIC executes multiplexed data streams inside UDP datagrams. Because parallel streams transfer independently, packet loss on one stream does not stall unrelated streams, eliminating the head-of-line blocking inherent to TCP-based HTTP/2.

## Standard Port Conventions and Protocol Dependencies
Application-layer services bind to well-known transport ports to accept incoming traffic. Security frameworks require knowing the default transport mappings, whether connections run plain or encrypted, and their underlying transport mechanisms.

| Port | Transport | Protocol / Service | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **21** | TCP | FTP | File transfer with separate control and data channels |
| **22** | TCP | SSH / SFTP | Secure shell remote access and encrypted file transfer |
| **23** | TCP | Telnet | Unencrypted remote command line (legacy) |
| **25** | TCP | SMTP | Mail server-to-server relay and submission |
| **53** | UDP / TCP | DNS | Domain-to-IP resolution (TCP for large payloads/zone transfers) |
| **67 / 68** | UDP | DHCP Server (67) / Client (68) | Dynamic host configuration and IP assignment |
| **80** | TCP | HTTP | Unencrypted web pages and basic REST calls |
| **110** | TCP | POP3 | Legacy email mailbox retrieval |
| **123** | UDP | NTP | Clock synchronization across distributed infrastructure |
| **139** | TCP | NetBIOS / IMAP* | NetBIOS session service and legacy message access (*source port binding) |
| **443** | TCP / UDP | HTTPS / HTTP/3 | Encrypted web traffic via TLS over TCP or QUIC over UDP |
| **445** | TCP | SMB | Windows network file sharing and IPC |
| **1521** | TCP | Oracle Database | Oracle DB client listener communication |
| **3360** | TCP | MySQL | Relational database client connections (variant port) |
| **3389** | TCP | RDP | Windows Remote Desktop Protocol graphical sessions |
| **5432** | TCP | PostgreSQL | Relational database communication |

Modern application protocols build on structured dependencies: web apps upgrade HTTP to bidirectional WebSocket streams for low-latency notifications; identity providers leverage OAuth 2.0 and OpenID Connect over HTTPS; and enterprise authorization relies on LDAP or LDAPS over TCP.

## Infrastructure, Security, and Traffic Management
Local routing and service availability depend on specialized intermediary layers:
- **Core and WAN:** SD-WAN centralizes branch-office routing policies via software orchestration rather than static hardware links.
- **Traffic Delivery:** Load balancers distribute compute load across server pools; reverse proxies front internal endpoints to handle SSL/TLS termination and static caching; API gateways enforce throttling and routing for downstream microservices.
- **Perimeter Defense:** Next-generation firewalls inspect application layer payloads; intrusion detection and prevention systems (IDS/IPS) identify and drop malicious packet sequences; VPNs (IPsec, WireGuard) establish encrypted tunnels between untrusted endpoints.
- **Identity & Governance:** Identity Providers (IdP) centralize authentication; PKI structures distribute digital certificates needed for TLS; SIEM and Network Management Systems (NMS) aggregate logs to identify bottlenecks and breaches.
- **Virtualization:** Network Functions Virtualization (NFV) replaces physical firewalls and routers with software appliances inside cloud hypervisors.

## Network Diagnostics Toolkit
When troubleshooting connectivity, latency, or protocol failures, targeted diagnostic commands isolate faults across physical, transport, and application layers:

| Diagnostic Need | Command | Action |
| :--- | :--- | :--- |
| **Basic Reachability** | `ping <target>` | Verifies ICMP round-trip time and packet reception. |
| **Path & Latency Drops** | `traceroute` / `mtr` | Identifies intermediary hops, highlighting latency spikes or dropouts. |
| **Interface Identity** | `ip addr` / `ip link` | Verifies local IP bindings, interface operational states, and MACs. |
| **Gateway & Routing** | `ip route` | Displays the kernel routing table and default next hop. |
| **Neighbor Discovery** | `ip neigh` | Inspects local ARP cache entries to detect IP-MAC mapping issues. |
| **Listening Ports** | `ss -tulpn` | Checks local open sockets, bound ports, and associated process IDs. |
| **DNS Resolution** | `dig <domain>` | Queries upstream resolvers to inspect raw DNS records. |
| **Web Service Checks** | `curl -I <url>` | Retrieves HTTP(S) response headers to check status codes and caching. |
| **Packet Inspection** | `tcpdump` / `tshark` | Captures live packet traces to inspect headers, flags, and payloads. |
| **Bandwidth Capacity** | `iperf3 -c <host>` | Measures raw throughput between two points without application overhead. |
| **Port & Service Audits**| `nmap <target>` | Scans open remote ports and fingerprints active listening services. |

## Common Mistakes
- **Confusing Modems and Routers:** Assuming a Wi-Fi router alone provides internet access. Routers merely manage local private subnets via NAT and DHCP; an active modem is required to translate physical ISP signals into routable data.
- **Using Hubs Instead of Switches:** Placing a legacy hub in high-density environments creates a single shared collision domain, causing widespread packet collisions and performance degradation compared to a switch's isolated per-port collision domains.
- **Selecting UDP for Loss-Sensitive Workloads:** Choosing UDP to eliminate TCP handshake latency for critical transactions (like file transfers or financial operations) without building an application-level acknowledgment mechanism, risking silent data loss.
- **Checking External Ports While Sockets Are Unbound:** Debugging remote firewalls and routing configurations before verifying via `ss -tulpn` that the target application daemon is actively listening on the expected interface and port.
- **Overlooking Multiplexing in HTTP/2 vs HTTP/3:** Assuming HTTP/2 over TCP eliminates all queue delays. Packet loss on a TCP link still stalls every parallel stream in HTTP/2 due to head-of-line blocking, a limitation solved by HTTP/3's stream-independent UDP-based QUIC engine.

---
*Source: Summary in our own words of 12 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
