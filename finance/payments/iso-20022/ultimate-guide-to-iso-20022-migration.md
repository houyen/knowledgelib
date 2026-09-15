---
id: finance/payments/iso-20022/ultimate-guide-to-iso-20022-migration
canonical_question: How do banks migrate legacy MT payment messages to ISO 20022 MX
  formats?
aliases:
- ISO 20022 migration guide
- MT to MX mapping
- SWIFT CBPR+ migration
- pacs.008 pacs.009 migration
- rich structured payment data
entity_type: migration_guide
domain: finance > payments > iso-20022
last_verified: '2026-09-15'
---

# The Ultimate Guide to ISO 20022 Migration in Financial Services

## 1. Overview & Executive Summary

1
Ultimate guide to ISO 20022 migration
Ultimate guide to
ISO 20022 migration
Deutsche Bank
Global Transaction Banking
3
Ultimate guide to ISO 20022 migration
Foreword
This is the watershed moment for the industry.
Over the next five years, the world’s primary payment
market infrastructures (PMIs) will undergo huge
transformational change in response to demands for
increased automation and cost efficiencies, enhanced
market integration and real-time services
These PMIs lie at the heart of the financial ecosystem, providing infrastructure
for High Value Payments Real Time Gross Settlement (RTGS) systems, Low
Value Payments Automated Clearing Houses (ACHs) and Real-Time Retail
Payment Systems.
As part of this transformational change, major PMIs such as the Federal
Reserve and The Clearing House (US), Eurosystem and EBA Clearing
(Eurozone) and the Bank of England’s RTGS (UK) will all modernise their High
Value Payment Systems (HVPS), almost simultaneously.
Underpinning each of those modernisation programs is the migration to ISO
20022, widely recognised as the standard for the future. Indeed, ISO 20022
has already been introduced for HVPS in Japan, Switzerland and China, and
is established as the de facto standard in instant payments markets following
implementations in Australia, US, Canada and Singapore. SWIFT will also
introduce ISO 20022 for cross-border payments, with a view to phasing out
existing payment messages.
The migration to ISO 20022 lays the foundation for vastly improved payment
processing efficiency and interoperability among HVPS. Its benefits are
numerous from a customer experience and compliance perspective, as well as
providing the capabilities to deliver new services.
This journey therefore has far-reaching implications for all banks, corporates
and other important financial stakeholders. It is probably the most impactful
payments industry undertaking since the introduction of the Single Euro
Payments Area (SEPA) more than a decade ago, and will require CEO
commitment, allocation of appropriate budgets, resources and project
teams given that a multitude of areas will be affected across institutions.
Senior management teams could also use this as a basis for reassessing
existing business models; at the very least, they should consider redesigning
substandard business processes.
This is not simply “another IT project”. Our series of guides on this topic,
produced in collaboration with PPI, aim to outline exactly what we can expect
between

---

## 2. Core Operational & Technical Architecture

SO 20022 migration
Figure 7: Migration of Euro, US dollar and Sterling regions to ISO 20022
2019 2020 2021 2022 2023 2024 2025
GlobalEuropeUKUS
Source: Deutsche Bank
4.1 Eurozone
Where do we stand?
Euro payments in the eurozone can be cleared on both a domestic and cross-
border basis via the respective payment systems:
1. Eurosystem*  TARGET 2: a RTGS system for the eurozone;
2. Eurosystem TARGET Instant Payment Settlement (TIPS): a payment system
for the processing of instant/real-time payments;
3. EBA**  EURO 1, operating on a multilateral net basis: a RTGS-equivalent large-
value payment system that settles single euro transactions of high priority and
urgency. It settles its end of day balances in central bank money via TARGET 2;
4. EBA STEP 2, for the processing of mass payments: This is a pan-European
Automated Clearing House (PE-ACH);
5. EBA RT1: a payment system for the processing of instant/real-time
payments. It provides the European payments industry with a pan-European
infrastructure platform for real-time payments in euro under the SEPA Instant
Credit Transfer scheme.
* Comprising ECB and central banks that have adopted the euro
** Owned by shareholders of the main European banks
ISO 20022 for cross-border
payments specifications
ISO 20022 guidelines
Introductory phase
ISO 20022
specifications
Preparation
phase
Development
phase
Legacy changes
(from Nov ‘20)
User
testing
p
Go-live
in
Nov ‘21
p
Go-live in
Nov ‘21
p
Go-live
in
‘22
4 years coexistence phase + SWIFT central translation service
From Q3 ‘23 only structured
address data for Parties
Enhance-
ment phase Mature phase
ISO 20022
like-for-like
+ 3 months
stability phase
ISO
enhance-
ment
phase
p
Go-live in
Nov ‘21
p
16
Ultimate guide to ISO 20022 migration
What’s the vision?
The Eurosystem has set out its “Vision 2020” on further integration of the
European financial markets3, initiating three projects to further develop the
market infrastructure:
1. TIPS;
2. The consolidation of TARGET 2 (T2) and TARGET2-Securites (T2S);
3. Eurosystem Collateral Management System (ECMS).
Going forward, the services provided by the Eurosystem will be named
TARGET Services, incorporating T2, T2S and TIPS. The technical
consolidation of T2 and T2S platforms, as well as the renewal of the RTGS
services, aim to increase efficiency, drive synergies, reduce operating costs
and boost cyber resilience. As part of this consolidation, the communication
mode will also change from the current single network provider via Y-copy to a
multi-network provider via the V-shape model. This requires future messages
to be addressed to the Eurosystem directly which, upon receipt, will use the
financial data not only for the settlement, but also initiate a new message for
the receiver based on the receiver’s reachability.
The T2/T2S consolidation will take place on the basis of ISO 20022 (T2S
has been using the standard since 2015). Hereby, the current decentralised
access to the individual central bank systems will be replaced by a central
entrance (see Figure 8). The consolidation has significant implications for all
T2 participants, fundamentally altering the entire handling of central bank
operations, minimum reserve requirements, payment transactions, secondary
systems and access to all T2 services.
Figure 8: New centralised access to T2 services
Central Liquidity Management
T2S
Securities
Settlement
RTGS
High-value
Payments
TIPS
Instant
Payments
Common Reference Data (CRD)
Shared Operational Services (Billing, Scheduler, etc)
Data Warehouse
Eurosystem Single Market Infrastructure Gateway
Source: Eurosystem
17
Ultimate guide to ISO 20022 migration
As with T2, EBA Clearing will also start with ISO 20022, and is currently
working on the respective guidelines for migration. The migration will take
place in form of a “Big Bang”.
Timeline for migration
Eurosystem participants have been informed that a “Big Bang” migration will
take place, with communication with the T2 system only possible via the n

---

## 3. Specifications, Standards & Lifecycle Operations

outlined in this paper, the ISO 20022 migration will
take years to fully implement and will not be without its
challenges. As such, our series of guides will keep you
abreast of all the latest developments and highlight key
points for consideration
Our next edition in this series will look at the migrations of the euro (with a
focus on T2/T2S consolidation and EBA Clearing), US dollar and sterling
areas, covering:
• An update on the most recent developments and communication
• Key changes to the status quo
• Project priorities and timelines
• Potential approach (tactical vs. strategic) depending on role of the bank
(direct participant, correspondent banking service provider, indirect
participant/correspondent banking user)
• Impact on the corporate customer
• Key challenges
• Final documentation
The next edition will also take a deep-dive look at SWIFT’s migration, providing:
• An update on the most recent developments and communication
• An update on decisions and output from CBPR+ and HVPS+
• Testing
• Translation/mapping rules
• Potential approach (tactical vs. strategic) depending on role of the bank
(correspondent banking service provider or correspondent banking user) as
well as impact on the corporate customer
• Key challenges
We hope that you find this series useful as you embark upon your own
migration journey.
Future editions 6
26
Ultimate guide to ISO 20022 migration
References
1  See SWIFT for ISO2022 presentation, https://www.slideshare.net/
SWIFTcommunity/swift-for-iso-20022-47105887
2  See “Economic analysis of SEPA” at pwc.com, https://pwc.to/2GaYUxS
3  See “The future of Europe’s financial market infrastructure: the Eurosystem’s
Vision 2020”, https://www.ecb.europa.eu/press/key/date/2015/html/
sp151014.en.html
4  See “Federal Reserve Announces ISO 20022 Migration Timeline for the
Fedwire Funds Service”, https://fedpaymentsimprovement.org/news/press-
releases/federal-reserve-announces-iso-20022-migration-timeline-fedwire-
funds-service/
5  See “SWIFT community to embark on migration to ISO 20022 for payments
traffic”, https://www.swift.com/news-events/news/swift-community-to-
embark-on-migration-to-iso-20022-for-payments-traffic
This document is for information purposes only and is designed to serve as a general overview regarding the services of Deutsche Bank AG, any of its branches and affiliates. The general description
in this document relates to services offered by Global Transaction Banking of Deutsche Bank AG, any of its branches and affiliates to customers as of April, 2019, which may be subject to change in
the future. This document and the general description of the services are in their nature only illustrative, do neither explicitly nor implicitly make an offer and therefore do not contain or cannot result
in any contractual or non-contractual obligation or liability of Deutsche Bank AG, any of its branches or affiliates. Deutsche Bank AG is authorised under German Banking Law (competent authorities:
European Central Bank and German Federal Financial Supervisory Authority (BaFin)) and, in the United Kingdom, by the Prudential Regulation Authority. It is subject to supervision by the European
Central Bank and the BaFin, and to limited supervision in the United Kingdom by the Prudential Regulation Authority and the Financial Conduct Authority. Details about the extent of our authorisation
and supervision by these authorities are available on request. Copyright© April, 2019 Deutsche Bank AG. All rights reserved

