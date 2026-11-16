---
id: software/system-design/bytebytego-archive-2025/authentication-sessions-jwt-sso-oauth
canonical_question: How do modern authentication and access control systems manage user identities, state, and permissions across distributed web applications?
aliases:
- cookies vs sessions vs jwt vs paseto
- web authentication and session management
- how sso and oauth2 work
- jwt vs paseto comparison
- rbac vs abac vs acl access control
- two factor authentication flow and factors
- stateless vs stateful authentication
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 11 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Modern Web Authentication and Access Control: Architecture, Mechanics, and Trade-offs

## TL;DR
Authentication verifies identity ("who are you"), while authorization establishes access rights ("what can you do"). Web systems balance stateful models like server sessions with stateless token primitives like JWT and PASETO depending on scaling and revocation requirements. Distributed architectures extend these primitives through Single Sign-On (SSO) and Multi-Factor Authentication (2FA) for identity federation, and enforce permissions using Role-Based (RBAC), Attribute-Based (ABAC), or Access Control List (ACL) models.

## State Management: Cookies vs. Server-Side Sessions

Web interactions run over stateless HTTP. To maintain identity across subsequent calls, applications rely on either client-retained cookies, centralized server sessions, or hybrid combinations.

* **Client-Side Cookies:** Small data payloads kept by the client's browser and transmitted with every outgoing HTTP request to the issuing domain. They offer straightforward transport for identifiers or claims, but exposing sensitive user payloads directly on the client invites credential leakage and tampering if transport security or browser flags are omitted.
* **Server-Side Sessions:** The server maintains user records in centralized memory or a database (such as active login timestamps and account profiles), issuing only an opaque reference string—a session ID—to the client, generally stored within a cookie. When incoming requests arrive, the server looks up the state via the ID. This offers fine-grained revocation control, but introduces storage bottlenecks and synchronization complexity across distributed server clusters.

| Criterion | Client-Side Cookie (Direct Data) | Server-Side Session (Opaque ID) |
| :--- | :--- | :--- |
| **Storage Location** | Client browser | Server memory/datastore (ID in cookie) |
| **Server Overhead** | Zero state storage | Memory and storage scale with user count |
| **Revocation Speed** | Difficult without expiration or blacklists | Immediate (invalidate session record on server) |
| **Distributed Systems** | Naturally stateless across nodes | Requires shared session store or stickiness |
| **Cross-Device Usability** | Poor portability across clients | Poor portability across distinct client apps |

## Token-Based Authentication: JWT and PASETO

Token-based approaches offload session lookup by encoding verifiable credentials directly into portable tokens transmitted via headers or payloads.

### JSON Web Tokens (JWT)
A standard formatting structure composed of three Base64URL-encoded segments separated by periods:
1. **Header:** Identifies the token type and the cryptographic algorithm employed to produce the signature.
2. **Payload:** The verifiable claims dataset containing standard registered claims, identity details, or system permissions.
3. **Signature:** A cryptographic proof formed by hashing the concatenated header and payload with a shared secret or a private key.

JWTs support two signing topologies:
* **Symmetric Signatures:** A single shared secret key is used both to sign and verify the token. Both the issuing service and verifying services must hold identical secrets.
* **Asymmetric Signatures:** The token issuer signs using a private key, while downstream consumers evaluate authenticity using a distributed public key.

### Platform-Agnostic Security Tokens (PASETO)
PASETO addresses design pitfalls in JWT, specifically eliminating cipher-suite negotiation vulnerabilities and weak defaults. Rather than permitting arbitrary algorithmic headers, PASETO enforces predefined versions and explicit operational modes:
* **Version:** Dictates the non-negotiable cipher suite in use.
* **Purpose:** Dictates whether the token is `local` (encrypted using symmetric cryptography for confidentiality and integrity) or `public` (signed using asymmetric cryptography for tamper-evident data without confidentiality).
* **Payload:** Contains the claims data, protected either by authenticated encryption or digital signature.

| Feature | Server-Side Sessions | JSON Web Tokens (JWT) | PASETO |
| :--- | :--- | :--- | :--- |
| **State Storage** | Centralized on server | Stateless (stored on client) | Stateless (stored on client) |
| **Payload Confidentiality** | High (payload hidden on server) | None by default (claims readable) | Guaranteed in `local` mode |
| **Algorithm Selection** | Application-defined | Configurable via header | Enforced by version/mode |
| **Validation Method** | Datastore index lookup | Cryptographic verification | Cryptographic verification |
| **Revocation Ease** | High | Low (valid until expiration) | Low (valid until expiration) |

## Federated Identity: Single Sign-On (SSO) and Delegation

Modern ecosystems frequently split identity providers from application services to centralize login workflows across multiple domains.

### Single Sign-On (SSO) Execution Flow
SSO lets a client authenticate once through a centralized Identity Provider (IdP) to access disparate Service Providers (SPs) like email, communication suites, or analytics dashboards:

1. **Initial Access:** A user requests a protected endpoint on an SP (e.g., Gmail). The SP notes an unauthenticated state and redirects the browser to the central IdP.
2. **Identity Verification:** The IdP detects no active global session, renders a login screen, and receives user credentials.
3. **Session Establishment & Token Issuance:** The IdP verifies credentials, creates an internal global session, generates a cryptographically signed token, and returns it to the browser.
4. **Token Handoff:** The browser routes the issued token back to the requesting SP.
5. **Validation:** The SP verifies the token against the IdP (confirming authenticity and validity) and renders the requested resource.
6. **Subsequent Application Traversal:** When the user subsequently navigates to a separate SP (e.g., Slack or YouTube), the second SP redirects to the IdP. The IdP observes the active global session, skips the password prompt, mints a scoped token for the new SP, and redirects the browser back to complete authorization without manual re-entry.

### Delegation and Alternate Authentication Primitives
* **OAuth 2.0:** Enables third-party systems to obtain bounded, delegated access to private user data without taking custody of raw account passwords.
* **QR-Code Authentication:** Encodes a unique, short-lived token into a matrix barcode rendered in a browser. A mobile device with an established identity scans the code, validates the underlying token with the server, and authorizes the desktop session without keyboard input.

## Multi-Factor Authentication (2FA/MFA)

Two-Factor Authentication enforces identity validation across multiple independent credential categories:
* **Knowledge Factor:** Something the user knows (passwords, PINs).
* **Possession Factor:** Something the user has (authenticator apps generating one-time passcodes, hardware RSA security keys).
* **Inherence Factor:** Something the user is (biometric readings like fingerprint or facial recognition).

A typical 2FA workflow requires the knowledge factor as step one. Upon matching the password, the server evaluates retry thresholds and demands the possession or inherence factor. Authenticator applications (such as Google or Microsoft Authenticator) and hardware security tokens offer stronger resistance to interception compared to SMS-based OTP delivery, which carries inherent risks of channel interception.

## Authorization Architectures: Enforcing Permissions

Once authentication identifies the user, access control architectures determine permissible actions across system assets.

| Mechanism | Structural Core | Best Use Case | Operational Trade-off |
| :--- | :--- | :--- | :--- |
| **Role-Based Access Control (RBAC)** | Roles (e.g., Admin, Viewer) mapped to collections of static actions. | Coarse-grained administrative domains with predictable user tiers. | Simple and scalable, but inflexible when decisions hinge on contextual data. |
| **Attribute-Based Access Control (ABAC)** | Dynamic policies combining user attributes, resource metadata, and environmental state (e.g., time, network location). | Complex, high-compliance environments requiring dynamic gating. | Exceptionally granular and flexible, but computationally intensive and complex to audit. |
| **Access Control Lists (ACL)** | Direct matrices mapping explicit users or service groups to individual assets. | File-system-like entities and dedicated multi-tenant object access. | Direct and intuitive per item, but administratively burdensome to maintain as user counts grow. |

## Common mistakes
* **Relying on SMS OTP for critical 2FA boundaries:** SMS delivery lacks end-to-end cryptographic integrity; authenticator apps or biometric devices provide substantially higher assurance.
* **Using unencrypted JWTs for confidential payloads:** Standard JWT payloads are Base64URL-encoded rather than encrypted, leaving claim data readable by any intermediary inspecting the token.
* **Assuming stateless tokens eliminate revocation requirements:** Unlike server sessions that can be purged instantaneously, tokens remain valid until expiration unless supplemental blacklists or refresh-token rotations are maintained.
* **Selecting arbitrary algorithms in token headers:** Permitting dynamic algorithm negotiation creates security vulnerabilities; systems should enforce strict cryptographic choices or adopt standards with safe defaults like PASETO.
* **Deploying complex ABAC when static roles suffice:** Introducing attribute-driven evaluation across simple systems incurs unnecessary engineering and performance overhead where static RBAC meets requirements.

---
*Source: Summary in our own words of 11 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
