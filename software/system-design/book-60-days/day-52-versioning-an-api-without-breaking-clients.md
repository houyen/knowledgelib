---
id: software/system-design/book-60-days/day-52-versioning-an-api-without-breaking-clients
canonical_question: Versioning an API Without Breaking Clients
aliases:
- System Design Day 52
- Versioning an API Without Breaking Clients
- Day 52 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 52: Versioning an API Without Breaking Clients

DAY 52 · SYSTEM DESIGN
Versioning an API Without Breaking Clients
Your API just shipped a breaking change.
/users now returns fullName instead of first_name + last_name. 3 mobile clients broke. 1 partner
integration went down. Your on-call is not happy.
You had a versioning strategy. It just wasn't the right one.
There are 4 ways to version an API. Here's what actually happens when you pick each one in production:
A — URL path versioning (/v1/users, /v2/users)
Simple. Explicit. Every request makes the version visible in logs and caches. But now you're maintaining 2
full route trees. A bugfix in the business logic layer has to be patched in both. Teams quietly let v1 rot.
B — Header versioning (API-Version: 2)
Clean URLs. Version negotiation in the transport layer, not the path. Harder to test in a browser, invisible in
logs unless you instrument for it, and clients forget to send the header — defaulting to whatever your
server decides "latest" means.
C — Query param versioning (/users?version=2)

---

DAY 52 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
D — Content negotiation: correct spec, wrong reality
Accept: application/vnd.api.v2+json is what the HTTP spec intended. You're asking for a specific
representation of a resource, not a different route. Semantically, it's the most correct.
In practice: Accept header parsing is inconsistent across client libraries. Middleware strips headers
silently. A misconfigured client gets a 406 Not Acceptable with no obvious error message pointing to
the version field. GitHub tried content negotiation early in their API and moved to URL versioning.
That tells you something.
