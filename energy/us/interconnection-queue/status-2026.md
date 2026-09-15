---
# === IDENTITY ===
id: energy/us/interconnection-queue/status-2026
canonical_question: "What is the current state of US electricity interconnection queues?"
aliases:
  - "interconnection backlog US"
  - "grid connection wait times"
  - "FERC interconnection queue delays"
  - "how long to connect to the grid"
  - "US grid queue capacity 2026"
  - "interconnection wait time years"
entity_type: situation_assessment
domain: energy > grid_infrastructure > interconnection
region: US
jurisdiction: US
temporal_scope: 2025-2026

# === VERIFICATION ===
last_verified: 2026-02-20
confidence: 0.92
freshness: monthly
version: 1.1
first_published: 2025-03-01

# === TEMPORAL VALIDITY ===
temporal_validity:
  status: evolving
  last_breaking_change: "2025-12-15"
  next_review: 2027-02-20
  change_sensitivity: medium

# === AGENT HINTS ===
inputs_needed:
  - key: stakeholder_type
    question: "What type of stakeholder are you?"
    type: choice
    options: ["solar developer", "wind developer", "storage developer", "utility/ISO", "policy researcher", "investor"]
  - key: region_focus
    question: "Which US region or ISO are you interested in?"
    type: text
  - key: timeline_horizon
    question: "What is your planning horizon?"
    type: choice
    options: ["near-term (1-2 years)", "medium-term (3-5 years)", "long-term (5+ years)"]

# === DISTRIBUTION ===
canonical_source: "https://knowledgelib.io/energy/us/interconnection-queue/status-2026"
suggested_citation: "Source: knowledgelib.io — AI Knowledge Library (verified 2026-02-20)"

# === RELATED UNITS ===
related_kos:
  related_to: []
  alternative_to: []
  depends_on: []
  solves: []

# === SOURCES ===
sources:
  - id: src1
    title: "Queued Up: 2024 Edition, Characteristics of Power Plants Seeking Transmission Interconnection (End of 2023)"
    author: Lawrence Berkeley National Laboratory
    url: https://emp.lbl.gov/publications/queued-2024-edition-characteristics
    type: primary_research
    published: 2024-04-01
    reliability: high
  - id: src2
    title: "FERC Order 2023 Final Rule"
    author: Federal Energy Regulatory Commission
    url: https://www.ferc.gov/media/order-no-2023
    type: government_regulation
    published: 2023-07-28
    reliability: authoritative
  - id: src3
    title: "2024 Annual Grid Connection Report"
    author: American Clean Power Association
    url: https://cleanpower.org/resources/grid-report-2024
    type: industry_report
    published: 2024-09-12
    reliability: moderate_high
  - id: src4
    title: "Queued Up: 2025 Edition, Characteristics of Power Plants Seeking Transmission Interconnection (End of 2024)"
    author: Lawrence Berkeley National Laboratory
    url: https://emp.lbl.gov/publications/queued-2025-edition-characteristics
    type: primary_research
    published: 2025-12-15
    reliability: high
  - id: src5
    title: "FERC Order 2023-A — Rehearing and Clarification"
    author: Federal Energy Regulatory Commission
    url: https://www.ferc.gov/explainer-interconnection-final-rule-2023-A
    type: government_regulation
    published: 2024-03-21
    reliability: authoritative
  - id: src6
    title: "DOE Section 403 Directive: Accelerating Interconnection for Data Centers"
    author: White & Case LLP (DOE analysis)
    url: https://www.whitecase.com/insight-alert/doe-directs-ferc-accelerate-interconnection-data-centers
    type: government_regulation
    published: 2025-10-23
    reliability: high
  - id: src7
    title: "PJM Completes Interconnection Reform Transition Cycle 1 Studies"
    author: PJM Interconnection
    url: https://insidelines.pjm.com/pjm-completes-interconnection-reform-transition-cycle-1-studies/
    type: industry_report
    published: 2025-09-20
    reliability: high
---

# US Interconnection Queue Status (2026)

## Summary

The US interconnection queue remains the primary bottleneck in energy transition deployment. As of end 2024, approximately **2,300 GW** of generation and storage capacity (~10,300 projects) sits in interconnection queues — down 12% from the prior year's ~2,600 GW peak, driven by historic withdrawal rates and fewer new requests. [src4] Despite this decline, the queue still far exceeds total installed US generation capacity. The median wait time from interconnection request to commercial operation has doubled from under 2 years (2000-2007) to over 4 years (2018-2024). [src4, src1]

A notable shift in 2024: natural gas capacity in the queue surged 72% year-over-year, while solar, storage, and wind capacity all declined. [src4] FERC Order 2023 reforms are now being implemented across ISOs, with cluster-based study processes replacing serial queues. [src2, src5]

## Key Facts

- Queue depth: ~2,300 GW total (1,400 GW generation + 890 GW storage), down 12% YoY [src4]
- Projects: ~10,300 actively seeking interconnection as of end 2024 [src4]
- Completion rate: Only ~13% of capacity entering the queue (2000-2019) reached commercial operation [src4]
- Withdrawal rate: 77% of historical queue capacity was withdrawn [src4]
- Median timeline: Over 4 years from request to operation; was under 2 years for projects built 2000-2007 [src4]
- Agreements pending: 408 GW has draft or executed interconnection agreements but has not yet reached commercial operations [src4]
- Proposed COD: 49% of total queue capacity (1,271 GW) targets commercial operation by end 2026 [src4]
- Technology mix (end 2024): Solar 956 GW (-12% YoY), Storage 890 GW (-13% YoY), Wind 271 GW (-26% YoY), Natural gas 136 GW (+72% YoY) [src4]
- Cost: Interconnection study costs alone range $50K-$2M+ depending on size and complexity [src3]

## Regulatory Context

FERC Order 2023 (issued July 2023, effective 2024) introduced cluster-based study processes, financial readiness requirements, and defined deadlines to reduce speculative applications and speed up interconnection studies. [src2] FERC Order 2023-A (issued March 2024) made minor clarifications but preserved the core reform framework. [src5]

**Regional implementation progress (2025):**
- PJM completed Transition Cycle 1 (September 2025): 130 requests representing ~17.4 GW (56% solar, 25% wind, 10% storage, 5% hybrid, 3% gas). Transition Cycle 2 (~46 GW) expected to complete by end of 2026. [src7]
- SPP cleared its entire legacy backlog dating back to 2018 by September 2025, transitioning to its Consolidated Planning Process. [src4]
- ISO New England's compliance was accepted by FERC in April 2025, with transitional cluster studies beginning late 2025. [src5]

**Data center / large load demand (new pressure):**
- DOE issued a Section 403 directive (October 2025) requiring FERC to establish rulemaking for large load interconnections (>20 MW), with a final rule deadline of April 30, 2026. [src6]
- ERCOT alone reported 226 GW of large load customers (77% data centers) in its queue as of November 2025 — a 258% increase from 63 GW at end of 2024. [src6]

## Causal Factors

1. Speculative applications: Low barriers to entry led to queue flooding — 77% of historical capacity was eventually withdrawn [src4, src2]
2. Transmission capacity: Insufficient grid buildout to absorb new generation [src3]
3. Study process: Serial study approach created cascading delays when projects withdrew [src2]
4. Workforce: Insufficient engineering staff at utilities and ISOs to process studies [src3]
5. Interconnection cost uncertainty: Study cost escalation deters smaller developers [src3]
6. Data center demand: Surging AI/data center power needs adding massive new load interconnection requests — ERCOT's large load queue grew 258% in one year [src6]

## Decision Logic

### If stakeholder is a solar or wind developer
→ Expect 4+ year timelines from application to operation. Budget for interconnection study costs of $50K-$2M+ and be prepared for potential cost escalation during the study process. Focus on areas with available transmission capacity. [src4, src3]

### If stakeholder is a storage developer
→ Storage represents ~890 GW in queue (39% of total capacity). Co-location with generation projects may provide faster interconnection paths. [src4]

### If stakeholder is evaluating natural gas projects
→ Natural gas queue capacity surged 72% YoY in 2024, reflecting growing data center and AI power demand. Competition for gas interconnection slots is increasing. [src4]

### If planning horizon is near-term (1-2 years)
→ Only projects with executed interconnection agreements (408 GW pool) are likely to reach operation. New applications filed today face 4+ year timelines. [src4]

### If planning horizon is long-term (5+ years)
→ FERC Order 2023 cluster reforms should reduce speculative applications and improve study processing times by 2027+. Transmission buildout remains the binding long-term constraint. [src2, src5, src3]

### If stakeholder is a data center developer
→ New FERC rulemaking on large load interconnection (>20 MW) is expected by April 2026. ERCOT's large load queue surged to 226 GW. Consider co-location with existing generation or "bring your own generation" programs (PJM). [src6, src7]

### If evaluating investment in queued projects
→ Only 13% of historical queue capacity reached operation; 77% was withdrawn. Prioritize projects that already have interconnection agreements — 408 GW of capacity is in this "near-ready" pool. [src4]

## Trend Direction

Mixed but cautiously improving. The 12% YoY decline in queue volume is a positive signal, though driven partly by withdrawals rather than completions. [src4]

Expect:
- FERC Order 2023 cluster reforms to reduce new speculative applications (2025-2026) — early results are positive (PJM Cycle 1 complete, SPP backlog cleared) [src2, src5, src7]
- Legacy backlog remains severe through ~2027 [src3]
- Natural gas and data center load interconnection demand surging — ERCOT large load queue grew 258% in one year [src4, src6]
- New FERC rulemaking on large load interconnection expected by April 2026 [src6]
- Transmission buildout is the binding constraint long-term [src3]

## Important Caveats

- Queue capacity ≠ built capacity: Most proposed projects will never be built (77% historical withdrawal rate) [src4]
- Regional variation: Queue conditions vary dramatically by ISO/RTO — national averages mask local extremes [src1]
- Study cost data is approximate and varies widely by project size, location, and grid conditions [src3]
- FERC Order 2023 implementation is ongoing; full impact on processing times will not be measurable until ~2027

## Related Units

*No related units currently available. Planned:*
- FERC Order 2023 Summary
- US Transmission Buildout Status
- US Renewable Deployment Barriers
