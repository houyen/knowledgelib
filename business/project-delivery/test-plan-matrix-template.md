---
id: business/project-delivery/test-plan-matrix-template
canonical_question: How do you plan which test types are required per functionality in an implementation project?
aliases:
- test plan template
- test type matrix
- unit UAT regression performance volume testing
- test strategy per feature
- mẫu kế hoạch kiểm thử
- ma trận loại kiểm thử
- kiểm thử hồi quy hiệu năng tải
- test environment ownership
entity_type: specification
domain: business > project-delivery
last_verified: '2026-11-15'
source_type: summary
source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.
---

# Test Plan Matrix — Template

## TL;DR
For each functionality, decide per test type: **required or optional, what exactly is verified, in which environment, and who owns it.** One table per functionality keeps the plan reviewable and makes gaps visible.

## Test types
| Type | Purpose | Usual environment | Usual owner |
|---|---|---|---|
| Unit | Individual logic works in isolation (calculations, validations, save/update) | Development / sandbox | Development team |
| User acceptance (UAT) | Real users can complete their business tasks | Quality / QA | Business key users of that area |
| Regression | Existing functions still work after the change | Quality / QA | QA team |
| Performance | Response time under expected load | QA or pre-production | Performance test team |
| Volume | Stability with large data sets or peak-season load | QA or pre-production | Performance test team |

## Table per functionality
| Test type | Required? | What is verified | Environment | Owner |
|---|---|---|---|---|
| Unit | Required | Cost, tax and income calculations return correct values | Dev | Developers |
| UAT | Required | Accountants can post expenses and export balances | QA | Finance key users |
| Regression | Required | Daily postings do not corrupt ledger data | QA | QA team |
| Performance | Required | Summary report generates in under 3 seconds | QA | Performance team |
| Volume | Optional | Year-end batch with 50,000+ transactions completes | QA | Performance team |

## Deciding required vs optional
| Make it required when | It can stay optional when |
|---|---|
| The function calculates money, tax, stock or legal data | The function is display-only with small data |
| Users depend on it daily or at period close | Volumes are small and bounded |
| It is an integration point or shared by other modules | A failure has an easy manual workaround |
| A seasonal or period-end peak exists (performance/volume) | Load is flat and low |

Unit, UAT and regression are normally required for everything. Performance and volume are decided per functionality; cross-module dashboards and peak-season processes need both, tested in an environment sized like production.

## Completing the plan
- Entry criteria: build complete, test data loaded, environment stable.
- Exit criteria per type: e.g. 100% of critical cases passed, no open Severity 1–2 defects.
- Defect severity definitions and turnaround targets.
- Test data: source, masking of personal data, refresh schedule.
- Schedule and sign-off roles.

## Common mistakes
- "Performance test: required" with no number to test against.
- UAT executed by the project team instead of business users.
- Regression scope not updated when shared components change.
- Volume tests run on a QA system far smaller than production, giving false confidence.

---
*Source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.*
