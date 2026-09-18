---
id: self-docs/integration/rbac-architecture-assessment-from-gemini
canonical_question: 'Architecture and technical specifications for Verification &
  Second Opinion: RBAC & Authorization Architecture'
aliases:
- 'Verification & Second Opinion: RBAC & Authorization Architecture'
- RBAC Architecture Assessment From Gemini
entity_type: architecture_explainer
domain: self-docs > integration
last_verified: 2026-09-17
---

# Verification & Second Opinion: RBAC & Authorization Architecture
**System:** Core System & HRIS Integration Platform (Go / Chi / Postgres / Next.js)  
**Date:** July 21, 2026  
**Document Type:** Architectural Review & Technical Risk Assessment

---

## Executive Summary

This document provides an independent, adversarial second opinion on the Role-Based Access Control (RBAC) and authorization architecture of the Core System System. It evaluates the four existing authorization decision mechanisms, structural risks, permission model tradeoffs, and separation-of-duties gaps.

Key findings indicate that while short-term operational mitigations (such as correlation logging) were appropriate, several core security choices—specifically **Default-Allow (Opt-Out)** permissions, **unvalidated handler self-filtering** in ESS routes, and **volatile audit logging**—present significant risk for a system processing sensitive PII and financial Core System data.

---

## 1. Evaluation of the Four-Mechanism Authorization Model

### Current Architecture
1. **Role + Role Hierarchy:** `roles.parent_role_id` via recursive CTE inside `getAppRoles`, cached in request context (`UserRolesKey`).
2. **Fine-Grained Permissions + Priority Tier:** `permissions` table with `roles.priority` tie-breaker. Evaluates under an **Opt-Out (Default-Allow)** policy.
3. **Company / Department Scope:** Attribute-based scope checked via route-specific middleware (`ResolveCompanyScope`, `ResolveDepartmentScope`).
4. **Super-Admin Bypass:** Identity allowlist that short-circuits all authorization layers.

### Assessment & Verdict
* **Threat Model Alignment:** Framing this as "four disjoint mechanisms" overstates runtime performance degradation (since roles are cached in context), but **understates maintainability and security risk**.
* **Developer Cognitive Load:** Requiring developers to manually chain 3 to 4 independent middleware layers per route declaration leads to silent security gaps (e.g., applying permission gates while omitting scope validation).
* **Decision Unification Strategy:** 
  * **Option A (Correlation Logging via `RequestID`):** Correct immediate operational fix. Resolves debugging friction without core refactoring risk.
  * **Option B (Top-of-Request Context Pre-calculation):** Should **not** be implemented as a complex pre-calculator due to route-dependent parameter scoping.
  * **Recommended Action:** Transition to a **Single Gateway Middleware Pattern** that invokes a unified policy evaluator interface inside a single middleware wrapper.

---

## 2. Default-Allow (Opt-Out) Permission Model

### Analysis
The system currently allows access to any newly introduced module or action by default if no explicit deny row exists for a role. This decision was historically made to prevent system lockout when permission tables were sparse.

### Verdict: Indefensible for Core System & PII Data
In a Core System system handling salary details, bank accounts, and national ID numbers, authorization failures **must fail closed (default-deny)**. Under default-allow, adding a new endpoint without seed permission rows inadvertently grants full access to all roles.

```
Current (Default-Allow):  [ New Module Added ] ──> [ No Permission Row ] ──> ALLOW (High Risk)
Target (Default-Deny):   [ New Module Added ] ──> [ No Permission Row ] ──> DENY  (Fail-Safe)
```

### Required Safeguards (If Migration is Deferred Short-Term)
1. **CI/CD Build-Time Guardrail:** Implement a static analyzer or `chi.Walk()` test that verifies every registered route/module has explicit baseline seed rows in migration scripts. **Fail the build if unseeded routes exist.**
2. **Shadow-Mode Default-Deny Metric:** Track `AuthzDefaultAllowFallbackTriggered` in logs whenever default-allow grants access where default-deny would have blocked it.
3. **Mandatory Deprecation Timeline:** Schedule a hard deadline to flip the system default to `DENY`.

---

## 3. Handler Self-Filtering & ESS Allowlist Vulnerabilities

### Assessment of the 16 Allowlist Routes
Relying on handlers to perform self-filtering without router-tier enforcement has already led to two IDOR-shaped vulnerabilities. Testing route registration via `chi.Walk()` only proves a route was intentionally placed on an allowlist—it **does not prove the handler logic is secure**.

### Critical Vulnerability Identified
Three ESS endpoints (`GET /ess/leave-details`, `/ess/timesheet-raw`, `/ess/attendance-calendar`) rely on client-supplied `X-HRIS-Cookie` headers or `filePath` query parameters without validating caller ownership against the JWT identity. This represents a critical IDOR / Path Traversal vector.

### Structural Elimination Plan
```
                    ┌──────────────────────────────────────────┐
                    │          Incoming HTTP Request           │
                    └────────────────────┬─────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │    Router-Tier Identity Context Gate     │
                    │   (Extracts & Validates JWT Subject ID)  │
                    └────────────────────┬─────────────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
       ┌──────────────────────────────────┐    ┌──────────────────────────────────┐
       │      Explicit Scope / Policy     │    │   Mandatory Subject Injector     │
       │            Middleware            │    │  (e.g., Enforce Subject Claim)   │
       └─────────────────┬────────────────┘    └─────────────────┬────────────────┘
                         │                                       │
                         └───────────────┬───────────────────────┘
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │              Handler Execution           │
                    │ (Operates ONLY on Context-Bound Subject) │
                    └──────────────────────────────────────────┘
```

1. **Eliminate Client Identity Headers:** Remove reliance on `X-HRIS-Cookie` for identity. Extract target identity strictly from validated JWT claims in `r.Context()`.
2. **`RequireSelfScope` Middleware:** Create a dedicated router-tier middleware for self-service endpoints that automatically asserts `context.Param("employee_id") == jwt.Subject`.

---

## 4. Separation of Duties (SoD) & RBAC Self-Configuration

### Analysis
Currently, administrative endpoints (`AssignRole`, `RemoveRole`, `UpdatePermissions`) write audit logs when an actor modifies their own role or permissions, but do not block the action.

### Verdict
While audit-only logging was a reasonable first step to evaluate usage across 12 `hr_admin` accounts, leaving it unblocked creates a permanent privilege escalation vector.

### Recommended Tiered Model
* **Hard Block Self-Escalation:** Instantly reject any request where `actor_id == target_user_id` or where the actor modifies permissions for a role they currently hold.
* **Dual-Control (Maker-Checker):** Require a secondary administrative approval for role assignments involving high-privilege roles (`hr_admin`, `payroll_admin`).

---

## 5. Critical Missing Risks & Blind Spots

### A. Non-Persistent Audit Logs (High Severity)
Deny-decision audit events write exclusively to `stdout`. Without persistent database storage or verified log shipping, process restarts eliminate all forensic audit history.
* **Fix:** Connect security audit logging to a persistent database table or buffer.

### B. Ineffective Row-Level Security (RLS)
The Go application connects to PostgreSQL as a superuser (`BYPASSRLS`), rendering database-level RLS on the `employees` table completely ineffective.
* **Fix:** Downgrade the application's database user to a non-superuser role (`payroll_app`) with constrained grants.

### C. JWT Claim Stale State
Roles are synchronized on the frontend only upon application mount. Permission revocations mid-session remain un-enforced on the client, and rely entirely on server-side re-checking.
* **Fix:** Introduce lightweight role/permission version hashing in Redis or database context for state-changing requests.

---

## Summary Action Matrix

| Priority | Risk Area | Identified Issue | Recommended Remediation |
| :---: | :--- | :--- | :--- |
| **P0** | **Data Isolation** | App runs as Postgres Superuser (`BYPASSRLS`) | Switch DB connection to standard `payroll_app` role. |
| **P0** | **Authorization Bypass** | ESS routes trust client `X-HRIS-Cookie` | Bind ESS handlers strictly to `r.Context()` JWT claims. |
| **P1** | **Permission Model** | Opt-Out / Default-Allow | Add CI/CD checks for permission seeds; schedule Default-Deny flip. |
| **P1** | **Audit Trail** | Deny-logs write to volatile `stdout` | Implement persistent DB-backed audit event logging. |
| **P2** | **Privilege Escalation** | Admin can self-assign roles (Audit-only) | Hard-block self-referential role/permission modifications. |
| **P3** | **Architecture** | 4 disjoint middleware calls per route | Consolidate route gates into a unified policy middleware wrapper. |

---

*Document generated automatically by Architectural Review Tooling.*
