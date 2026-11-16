---
id: business/project-delivery/post-implementation-review-template
canonical_question: How do you structure a post-implementation review (PIR) report after go-live?
aliases:
- post-implementation review
- PIR report
- lessons learned
- hypercare review
- root cause and resolution
- đánh giá sau triển khai
- bài học kinh nghiệm dự án
- báo cáo sau go-live
- project retrospective
entity_type: specification
domain: business > project-delivery
last_verified: '2026-11-15'
source_type: summary
source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.
---

# Post-Implementation Review (PIR) — Template

## TL;DR
Run the PIR after the stabilisation period (commonly 30 days). Three sections: **what users reported and its impact**, **why it happened and how it was resolved**, **lessons turned into changes to the delivery method**. A lesson that does not change a template, checklist or plan is only an observation.

## Section 1 — Feedback: issues and impact
| Issue | Priority | Business impact (quantified) |
|---|---|---|
| Mobile scanning errors and slow response in the warehouse | High | 25% delay in inbound clearing during week one |
| Automatic invoice extraction fails for ~8% of documents | Medium | Manual handling by accounts payable; slower weekly clearing |
| Reports slow during period close | Medium | Management reporting delayed by hours |
| Users ignore pre-filled templates | Low | 10–15 minutes lost per order |

Rules: collect from tickets, surveys and floor observation; state impact as a number; rank by priority, not by who complained loudest.

## Section 2 — Likely reasons and resolutions
| Issue | Root cause | Resolution |
|---|---|---|
| Scanning | Too little hands-on practice; weak wireless coverage | On-site coaching, simplified input screens, network upgrade |
| Invoice extraction | Non-standard layouts, low-quality scans | Tune extraction templates; publish a submission guide for suppliers |
| Report performance | Heavy analytical queries during transaction peaks | Optimise views/indexes; schedule batch analytics off-peak |
| Template under-use | Users unaware of the shortcut | Short video guides; make templates the default |

Separate cause categories: people/training, process, data, technology, external parties. Most post-go-live issues are not software defects.

## Section 3 — Lessons learned and how they are embedded
| Lesson | Change to the method |
|---|---|
| Classroom training does not prepare operators for physical tools | Training framework requires ≥ 50% hands-on simulation in a staging environment |
| Master-data quality decides cutover success | Start data profiling and cleansing in the first project phase |
| External partners need early onboarding | Add a partner-enablement workstream with sandbox testing 4 weeks before cutover |

## Also include
- Benefits check: target KPIs from the business case versus actuals.
- Open items with owner and date, handed to operations.
- Budget and schedule versus plan, with reasons for variance.
- Recommendation: close the project, extend hypercare, or start a follow-up phase.

## Common mistakes
- Review held too early (issues still emerging) or too late (people have moved on).
- Blame-oriented discussion; nobody reports real causes.
- Lessons filed in a document nobody reads instead of changing the standard templates.

---
*Source: Generalised from the author's own coursework for an ERP implementation consultant programme (fictional case studies). Structure and thresholds are illustrative defaults to adapt, not a vendor standard.*
