---
id: software/system-design/bytebytego-archive-2025/web-security-https-firewall-injection
canonical_question: How do core web security mechanisms work across transport encryption, network firewalls, and application vulnerabilities?
aliases:
- how https and tls work
- http vs https handshake steps
- network vs host firewall differences
- sql injection types and techniques
- cross site scripting attack variants
- symmetric vs asymmetric encryption in tls
- web application security fundamentals
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Web Security Fundamentals: Transport Encryption, Firewalls, and Application Attacks

## TL;DR
Web security operates across multiple layers: securing data in transit, defending network perimeters, and safeguarding application logic. HTTPS combines asymmetric key exchange with symmetric session encryption over a verified TCP connection to prevent interception and tampering. Firewalls enforce traffic boundaries across OSI layers at both network and host levels, while application safeguards prevent attackers from abusing input channels through SQL injection (SQLi) or cross-site scripting (XSS).

## Transport Security: HTTP vs. HTTPS and the TLS Handshake
Standard HTTP transmits payloads as unencrypted plain text across a standard three-way TCP handshake (SYN, SYN-ACK, ACK). Any intermediary on the wire can inspect sensitive credentials, authentication tokens, and user inputs. HTTPS resolves this by running HTTP over Transport Layer Security (TLS), wrapping communication in an encrypted tunnel.

The establishment of an HTTPS session occurs in four sequential stages:

1. **TCP Handshake:** The browser and server establish a standard TCP connection prior to any cryptographic negotiation.
2. **Certificate Check and Protocol Negotiation:** The client issues a "client hello" detailing supported cipher suites and its highest supported TLS version. The server replies with a "server hello" selecting the mutually supported cipher suite and protocol version, accompanied by its digital certificate. The client validates the certificate, checking expiration dates, domain matching, and signatures from trusted Certificate Authorities (CAs).
3. **Asymmetric Key Exchange:** Once the certificate is validated, the client generates a unique symmetric session key, encrypts it using the server's public key (retrieved from the certificate), and sends it to the server. Only the server can decrypt this message using its corresponding private key. A "change cipher spec" message signals that both parties will encrypt subsequent traffic with this shared key.
4. **Symmetric Data Transmission:** Both endpoints now possess the identical session key and transmit bidirectional data using symmetric encryption.

HTTPS uses a hybrid cryptographic design rather than sticking to one method throughout the session:

* **Security Limits of Asymmetric Encryption:** Asymmetric cryptography is mathematically one-directional when using a public key for encryption. If the server were to encrypt response data with its private key, any client or observer holding the publicly distributed key could decrypt the response, destroying confidentiality.
* **Performance Overhead:** Public-key cryptography requires intense mathematical computation. Running asymmetric operations for every packet in high-throughput or long-lived sessions would overwhelm server resources. Symmetric encryption requires vastly less computational overhead, making it well-suited for high-volume data streams.

| Attribute | HTTP | HTTPS |
| :--- | :--- | :--- |
| **Transmission Mode** | Plain text | Encrypted binary stream (TLS) |
| **Connection Setup** | Single TCP handshake (SYN, SYN-ACK, ACK) | TCP handshake followed by TLS negotiation |
| **Identity Verification** | None | Cryptographic certificates verified by CAs |
| **Encryption Type** | None | Hybrid (Asymmetric exchange, symmetric transport) |
| **Data Confidentiality** | Insecure (vulnerable to eavesdropping) | Secure (confidential bi-directional channel) |

## Perimeter Defense: Network vs. Host-Based Firewalls
Firewalls serve as primary network checkpoints, filtering inbound and outbound packets against defined rules such as IP addresses, protocols, ports, applications, or specific keywords. Comprehensive protection uses a multi-layered model combining network-level and host-level inspection.

* **Network Firewalls:** Positioned at the network perimeter between internal infrastructure and the public internet, these firewalls operate primarily at OSI Layers 3 and 4 (Network and Transport layers). Implemented as hardware appliances, virtual appliances, or cloud services, they filter traffic based on source/destination IPs, ports, and protocols before incoming packets reach internal routers or servers.
* **Host-Based Firewalls:** Deployed directly as software agents on individual endpoints (such as employee laptops or individual backend servers), these firewalls operate from OSI Layer 3 through Layer 7 (Application layer). They perform deeper packet analysis and can enforce policies specific to local processes and applications.

| Feature | Network Firewall | Host-Based Firewall |
| :--- | :--- | :--- |
| **Deployment Location** | Network perimeter / edge | Individual machines, laptops, and servers |
| **OSI Layers** | Layer 3 to Layer 4 | Layer 3 to Layer 7 |
| **Inspection Scope** | IP addresses, protocols, ports | Deep packet inspection, local applications, ports, IPs |
| **Protection Boundary** | Entire internal network | Single device |
| **Implementation Form** | Physical hardware, virtual machine, or cloud service | Software running inside the operating system |

## Application Vulnerabilities: SQL Injection and Cross-Site Scripting
Even with encrypted transit and active firewalls, applications remain susceptible if they fail to validate and sanitize user inputs before processing them.

### SQL Injection (SQLi)
SQL injection occurs when unvalidated user input alters database query logic, giving unauthorized parties access to backend records:

* **Basic (Tautology-based):** Injects boolean tautologies (such as `1=1`) into queries to invalidate conditional statements, allowing attackers to bypass authentication gates or dump entire tables.
* **In-Band (Union/Error-based):** Leverages operators like `UNION SELECT` to append unauthorized query results to normal responses, or intentionally triggers database errors that reveal sensitive fields and schema structure in error outputs.
* **Blind (Boolean-based):** Used when the application suppresses query results and database errors. The attacker injects queries that force true or false states, observing subtle differences in whether the webpage renders normally.
* **Blind (Time-based):** Injects time-delay operations (such as `SLEEP(5)`) to measure server response latency, systematically verifying database contents based on delayed responses.

### Cross-Site Scripting (XSS)
Cross-Site Scripting involves injecting executable scripts into web pages viewed by other users, allowing attackers to hijack sessions, extract session cookies, or manipulate page behavior:

* **Reflected XSS:** The malicious payload is embedded inside request parameters or URLs and reflected immediately in the server's HTTP response. This vector relies on social engineering, requiring victims to click malicious links.
* **Stored XSS:** The script is permanently persisted in the server's database (such as within forum comments, review sections, or profile fields). Whenever any client requests that stored content, the malicious script executes automatically in their browser.
* **DOM-based XSS:** The attack executes entirely on the client side. The payload modifies the browser's Document Object Model directly through client-side scripts, never reaching the server's backend processing pipeline.

| Vulnerability Type | Primary Target | Delivery Mechanism | Impact |
| :--- | :--- | :--- | :--- |
| **SQLi (Basic & In-Band)** | Database engine | Query parameters, form inputs | Unauthorized data extraction, authentication bypass |
| **SQLi (Blind)** | Database engine | Conditional logic, injected sleep delays | Incremental data exfiltration without visible errors |
| **Reflected XSS** | Client browser | Crafted links, malicious URLs | Cookie theft, session hijacking on click |
| **Stored XSS** | Client browser | Persisted database entries (comments, profiles) | Automated script execution on all viewers |
| **DOM-based XSS** | Client browser | Client-side DOM modification | Browser manipulation bypassing server validation |

## Common Mistakes
* **Attempting to use asymmetric encryption for full data transmission:** Relying solely on asymmetric keys causes severe server performance degradation due to heavy cryptographic math and compromises return traffic confidentiality, since anyone holding the server's public key could decrypt server-to-client payloads.
* **Relying entirely on network firewalls without host firewalls:** Network firewalls inspect traffic only up to Layer 4 at the edge; omitting host-level Layer 7 firewalls leaves machines unprotected if traffic passes the perimeter or originates internally.
* **Assuming blind SQLi is low risk due to suppressed errors:** Attackers do not need visible query output or database error dumps; time delays such as `SLEEP(5)` or boolean response shifts allow complete data extraction.
* **Relying solely on server-side filters to catch all XSS:** Server-side sanitization cannot intercept DOM-based XSS payloads that execute directly inside browser scripts without ever touching the web server.
* **Skipping certificate authority (CA) verification in client applications:** Bypassing expiration checks, domain matching, or CA trust chains during the TLS handshake neutralizes the identity verification step, leaving clients open to interception.

---
*Source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
