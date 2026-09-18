---
id: self-docs/security/rbac-second-opinion-analysis-from-gpt
canonical_question: Architecture and technical specifications for Independent Second
  Opinion on RBAC/Authorization Architecture
aliases:
- Independent Second Opinion on RBAC/Authorization Architecture
- RBAC Second Opinion Analysis From GPT
entity_type: architecture_explainer
domain: self-docs > security
last_verified: 2026-09-17
---

# Independent Second Opinion on RBAC/Authorization Architecture

## Executive Summary

Priority ranking:

1. Default-allow authorization model (**Critical**)
2. Handler self-filtering authorization boundary (**Critical**)
3. Self-RBAC administration / SoD (**High**)
4. RLS ineffective due to BYPASSRLS (**High**)
5. Unified AuthDecision abstraction (**Medium**)
6. Audit log persistence (**Medium**)
7. Frontend stale permissions (**Low**)

## 1. Four authorization mechanisms

The system does not have four separate authorization systems. It has four authorization **dimensions** whose evaluation is fragmented.

This is primarily a maintainability and observability problem rather than a direct security flaw.

### Recommendation

Keep structured logging (Option A).

Defer a unified `AuthDecision` object until a broader router/auth refactor instead of implementing it immediately.

## 2. Default-Allow Permission Model

For a Core System system, default-allow is not an appropriate long-term security posture.

Historical reasons are understandable, but the policy should not become permanent.

### Minimum mitigation if migration is deferred

- CI test requiring explicit permission rows for every new module/action.
- Explicit metadata indicating permission requirements.
- Shadow-mode execution comparing current vs future default-deny decisions before switching.

## 3. Handler Self-Filtering

The coverage test is valuable but only detects symptoms.

The architecture has already produced multiple authorization bugs of the same pattern.

Identity ownership checks should move into reusable middleware or authorization helpers instead of relying on every handler.

## 4. Separation of Duties

Given twelve HR administrators exist, preventing self-role escalation is likely practical.

Audit-first is reasonable temporarily, but prevention should become the long-term objective unless operational constraints require otherwise.

## 5. Additional Risks

### Permission semantics

Document precedence rules for:

- allow vs deny
- inherited permissions
- multiple parent roles
- multiple assigned roles
- priority interactions

### Route coverage

Route coverage is not equivalent to authorization coverage.

Add semantic integration tests.

### JWT lifecycle

Document role refresh and revocation behavior.

### Route classification

Every route should explicitly declare one of:

- Public
- Authenticated
- Self
- Role
- Permission
- Internal

No uncategorized routes.

### RLS

Running the application using a PostgreSQL role with BYPASSRLS largely eliminates the intended defense-in-depth provided by Row-Level Security.

## Overall Conclusion

The architecture has improved significantly through iterative hardening.

The highest priorities should now be:

1. Plan migration toward default-deny.
2. Eliminate handler-level ownership enforcement patterns.
3. Address ineffective RLS deployment.
4. Continue improving observability while deferring major AuthDecision refactoring until a larger architectural change.
