---
id: software/architecture/software-architecture/conways-law-product-lines-reference-architecture
canonical_question: How do Conway's Law, software product lines and reference architectures affect how you organise teams and reuse architecture?
aliases:
- Conway's Law
- software product line
- product family
- reference architecture
- commonalities and variations
- team structure and architecture
- định luật Conway
- dòng sản phẩm phần mềm
- kiến trúc tham chiếu
- tái sử dụng kiến trúc
entity_type: book_chapter
domain: software > architecture > software-architecture
last_verified: '2026-11-15'
source_type: summary
source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.
---

# Conway's Law, Product Lines and Reference Architecture

## TL;DR
Systems end up shaped like the organisations that build them, so plan the architecture first and form teams around it. When several products share most of their behaviour, treat them as a **product line** built on a **reference architecture**, separating what is common from what varies.

## Conway's Law
A system's structure tends to mirror the communication structure of the organisation producing it. It is an observation, not a law of nature, but it is reliable enough to plan with.

| Implication | Practice |
|---|---|
| Team boundaries become component boundaries | Decide the target architecture, then assign teams to components (e.g. one per tier or per service) |
| Interfaces form where teams talk least | Make those interfaces explicit contracts |
| Cross-cutting needs get orphaned | Create a team responsible for shared services and consistency |
| Reorganising teams changes the system | Treat org changes as architectural changes |

## Product lines
A product line is a set of products sharing a common base, giving lower cost per product, a consistent user experience, and shorter time to market. It needs up-front investment, so it rarely pays for one or two products unless more are planned.

### Splitting the work
| Activity | Scope |
|---|---|
| Domain engineering | Build the shared base: commonalities, variation points, reference architecture |
| Application engineering | Build each product on that base, filling in the variations |

### Classify every feature
| Class | Meaning | Design consequence |
|---|---|---|
| Commonality | Same in every product | Lives in the shared base |
| Variation | Differs between products | Needs an explicit variation point |
| Product-specific | Exists in one product only | Stays outside the base |

### Three ways to realise variation
| Technique | How |
|---|---|
| Adaptation | A component changes behaviour through configuration or settings |
| Replacement | A default component is swapped for an alternative (or a gap must be filled) |
| Extension | A common interface lets add-ons be attached |

## Reference architecture
The shared architecture a product line's products build on, so no product starts from scratch. It must support the variations while keeping the commonalities stable. Infrastructure and platform services are natural candidates for the common base.

## Applying it to enterprise delivery
- One implementation rolled out to several subsidiaries or countries is a product line: common core, country-specific variation points (tax, calendar, language), entity-specific extensions.
- Decide for each requirement which of the three classes it is **before** building; variations discovered late become forks.
- Give the common base one owner. Without it each rollout drifts and reuse disappears.

---
*Source: Summary in our own words of *Software Architecture — Course Notes* (University of Alberta, Software Design and Architecture specialization). Not a verbatim copy.*
