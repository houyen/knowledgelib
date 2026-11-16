---
id: business/project-delivery/go-no-go-decision-matrix-template
canonical_question: How do you build a go/no-go decision matrix for a system go-live or cutover?
aliases:
- go no-go decision matrix
- go-live readiness
- cutover decision
- go-live criteria
- rollback trigger
- ma trận quyết định go no-go
- tiêu chí go-live
- sẵn sàng vận hành
- cutover checklist
entity_type: specification
domain: business > project-delivery
last_verified: '2026-11-15'
source_type: summary
source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.
---

# Go/No-Go Decision Matrix — Template

## TL;DR
Decide the rules **before** the cutover weekend, as numbers. A go/no-go matrix has three parts: major risks with thresholds, anticipated cutover issues with pre-agreed responses, and mandatory readiness parameters. During cutover nobody negotiates; they look up the rule.

## Part 1 — Major risks and decision rules
| Risk | Measure | Rule (example defaults) |
|---|---|---|
| Data migration integrity | Automated reconciliation accuracy | NO-GO below 99.5% until cleansing is complete |
| Critical defects | Open defects by severity | NO-GO with any Severity 1, or more than 3 Severity 2 without approved workaround |
| Infrastructure / latency | Response time in peak simulation | NO-GO above the agreed latency ceiling for remote sites |

## Part 2 — Issues that may occur during the cutover window
Write each as *issue → GO condition → NO-GO / rollback condition*.

| Issue | Proceed (GO) if | Stop (NO-GO / rollback) if |
|---|---|---|
| Cutover runs late | Slippage is inside the buffer and catch-up steps recover it | Delay exceeds the point where business start is at risk |
| External interface fails (bank, tax, partner) | Fixed inside the remediation window, or a manual fallback safely covers the first days | No safe manual fallback |
| Key person unavailable | Named backup is mobilised and briefed in time | No qualified backup for a required sign-off |
| Balance reconciliation discrepancy | Difference is immaterial and logged for post-go-live adjustment | Difference affects financial or stock-critical items |
| Production smoke test failure | Fault is isolated and fixed on the spot | A core service is unstable |

## Part 3 — Readiness parameters (all mandatory)
| Parameter | Evidence | Threshold |
|---|---|---|
| Business UAT sign-off | Written sign-off from every stream lead | 100% |
| End-user training | Verified completion rate | ≥ 95% |
| Rollback and disaster recovery | Plan approved; restore dry-run executed | Documented and tested |
| Hypercare support | Command centre, ticketing, escalation contacts live | Operational before go-live |

## How to use
1. Draft with stream leads 3–4 weeks before cutover; get steering committee approval.
2. Assign one owner per row who reports status as green/amber/red with evidence.
3. Hold formal checkpoints: T-7 days, T-1 day, and at each cutover milestone.
4. Record the decision, who made it, and the evidence. A conditional GO lists the conditions and their deadlines.
5. Define the **point of no return** and the rollback duration; the last NO-GO checkpoint must sit before it.

## Common mistakes
- Criteria phrased as "acceptable" or "stable" instead of numbers.
- No rule for partial failure, so the decision is argued at 3 a.m.
- Rollback plan never rehearsed.
- Readiness judged by the project team alone, without business owners.

---
*Source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.*
