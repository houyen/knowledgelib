---
id: finance/payments/clearing-settlement/rbi-payment-and-settlement-systems-architecture
canonical_question: How do modern national payment and settlement systems (RTGS, instant
  retail, batch clearing) operate at scale?
aliases:
- RBI payment and settlement systems
- RTGS architecture
- NEFT batch settlement
- UPI retail payment architecture
- national clearing house NACH
entity_type: central_bank_monograph
domain: finance > payments > clearing-settlement
last_verified: '2026-09-15'
---

# National Payment & Settlement Systems Architecture: RTGS, NEFT, UPI, and NACH

## 1. Overview & Executive Summary

Payment and
Settlement Systems in India
Journey in the
Second Decade of the
Millennium
201 0
20
.
Foreword
"Take up one idea. Make that one idea your life; think of it; dream of it;
live on that idea. ... This is the way to success." - Swami Vivekananda1.
This Booklet is a narrative of how the carefully thought out steps taken
by the Reserve Bank of India (RBI) have resulted in transforming India into
a country riding the crest of a wave in the evolution of digital payments.
Chief among those steps was the conceptualisation and establishment of
institutions - Institute for Development and Research in Banking Technol-
ogy (IDRBT), National Payments Corporation of India (NPCI) and Clearing
Corporation of India Limited (CCIL) - that laid the foundation of India's
payment systems. The bouquet of digital payment products that is now
available in the country and that enriches the consumer experience with
choices, convenience and confidence in the digital payment ecosystem,
owes a lot to these institutions.
Over the course of this journey, significant upgradation was achieved by
way of enhancement of acceptance infrastructure, boost to financial
inclusion and adoption of digital modes for Government payments backed
by the national identity authentication, Aadhaar framework. To win the trust
of customers, an expanding payment system was overlaid with a reliable
supervision and settlement mechanism. Interoperability among payment
systems facilitated unparalleled ease of transactions while robust customer
protection measures have made India's retail payment system one of the
safest in the world.  The journey has only just begun, but India is already
seen as a player at the global forefront in the domain of digital payments.
This Booklet, which focusses on the decade 2010-20, gives the legal and
regulatory environment underpinning the digital payment systems, the
various payment system choices available to consumers, extent of usage
and so on. The Booklet also takes up a self-analysis of the domains
explored and territories not charted through the course of this journey. To
place things in perspective, an exercise was undertaken in 2019 to
benchmark India's payment systems with 20 other countries.
1  Karma-Yoga: On Life, Work and Spirituality, by Swami Vivekananda
While realising that 'well begun is half done', RBI is mindful of the
challenges ahead. Various initiatives are underway to realise India's vision
on payment systems. RBI seeks to usher in a payment ecosyst

---

## 2. Core Operational & Technical Architecture

ms in India | 63
from November 19, 2018.
Continuous Linked Settlement (CLS)
14.8 CCIL offers non-guaranteed settlement of cross currency transactions
through CLS Bank on a PVP basis. The settlement is through a third party
arrangement.
Directions for central counterparties (CCPs)
14.9 Directions on governance of domestic CCPs authorised to operate
in India by RBI: Governance provides the processes through which an
organisation sets its objectives, determines the means for achieving those
objectives, and monitors performance against the objectives. To ensure
appropriate governance standards in CCPs, RBI issued directions on the
broad principles underlying governance of CCPs covering the composition
of the board, roles and responsibilities of the board, appointment of
Directors, constitution of Committees, etc.
14.10
Directions on networth requirements and ownership of CCPs: CCPs
should have sufficient networth to cover potential general business losses
and continue to provide services as a going concern. RBI stipulated a
networth of ` 300 crore for authorisation / recognition of any CCP desirous
of operating in India. Further, in line with the Principles for Financial Market
Infrastructures (PFMIs), CCPs are required to hold liquid net assets funded
by equity capital equal to minimum of six months of current operating
expenses. With regard to ownership of the CCP, shares of an authorised
CCP  can be held only by persons who are users of the authorised CCP.
CCIL is compliant with the requirements laid out for networth and ownership
of CCPs.
_______
64 | Payment and Settlement Systems in India
15.1 Settlement can be defined as the process of transferring of funds
through a central agency, from payer to payee, through participation of their
respective banks or custodians of funds. The two key elements for payment
processing are payment order or message requesting the transfer of funds
to the payee and the actual transfer of funds between the payer's bank
and the payee's bank. Settlement systems can be classified based on (i)
time - designated-time (or deferred) settlement systems and real-time (or
continuous) settlement systems and (ii) amount - gross settlement and net
settlement. India has multiple payments and settlement systems, for both
gross and net settlement systems.
15.2 Participants in PSS are exposed to two risks that need to be
addressed, viz., credit risk and liquidity risk. Credit risk, which may occur
due to default of a counterparty, is the risk that a counterparty will not meet
an obligation when due. Liquidity risk is when a counterparty will fail to
settle an obligation for full value when due, but will do so at some
unspecified time thereafter. Both credit and liquidity risks together constitute
settlement risk.
Gross Settlement
15.3 A gross settlement system is one in which the settlement or funds
transfer occurs individually as and when each payment transaction is
processed in the system. Each transaction is settled on a one-to-one basis
without bundling or netting with any other transaction.  In some countries,
there are systems in which the final settlement of transfers occurs at the
end of the processing day without netting the credit and debit positions on
a transaction-by-transaction basis. Such systems are called end-of-day
gross settlement systems. In the RTGS systems, usually operated by a
country's central bank as it is seen as a critical infrastructure for a country's
economy , the inter-member payments settle on a 'real' time and a 'gross'
basis in the books of the central bank.
15.4 Since RTGS does not have a settlement lag, it eliminates settlement
risk. The liquidity risks in RTGS are managed through IDL extended to
Chapter 15
Settlement Processes
Payment and Settlement Systems in India | 65
members by RBI against fully collateralised Indian government securities
held by the members in their IDL-SGL account. IDL is extended free of
interest. IDL has to be reversed by the end of the day and failu

---

## 3. Specifications, Standards & Lifecycle Operations

Discount Rate
76 MeitY Ministry of Electronics and Information Technology
77 MIBOR Mumbai Inter Bank Offer Rate
78 MICR Magnetic Ink Character Recognition
79 MIOIS Mumbai Inter Bank Overnight Indexed Swaps
80 MMBCS Magnetic Media Based Clearing System
81 MNSB Multi-lateral Net Settlement Batch
82 MoU Memorandum of Understanding
83 MPoS Mobile Point of Sale
84 MSME Micro, Small and Medium Enterprise
85 MTSS Money Transfer Service Scheme
86 NACH National Automated Clearing House
87 NCD Non-Convertible Debenture
88 NCMC National Common Mobility Card
89 NDS-OM Negotiated Dealing System-Order Matching
90 NECS National Electronic Clearing Service
91 NEFT National Electronic Funds Transfer
92 NETC National Electronic Toll Collection
93 NFC Near Field Communication
94 NFS National Financial Switch
95 NG-R TGS Next Generation-Real Time Gross Settlement
96 NPCI National Payments Corporation of India
97 NSBL Nep al SBI Bank Limited
124 | Payment and Settlement Systems in India
Sl No Acronym Exp ansion
98 ODR Online Dispute Resolution
99 OTC Over The Counter
100 P2M Person to Merchant
101 P2P Person to Person
102 PA Payment Aggregator
103 PAN Primary Account Number
104 PBs Payment Banks
105 PDC Private Digital Currency
106 PFMIs Principles for Financial Market Infrastructures
107 PG Payment Gateway
108 PIDF Payment s Infrastructure Development Fund
109 PIN Personal Identification Number
110 PKI Public Key Infrastructure
111 PM Performance Metrics
112 PoA Point of Arrival
113 PoS Point of Sale
114 PPI Prepaid Payment Instrument
115 PRD Panel for Resolution of Disputes
116 PSO Payment System Operator
117 PSP Payment System Provider
118 PSS Payment and Settlement Systems
119 PSTN Public Switched Telephone Network
120 PSU Public Sector Undertaking
121 QCCP Quantified Central Counterparty
122 QR Quick Response
123 RBI Reserve Bank of India
124 RDA Rupee Drawing Arrangement
125 RECS Regional Electronic Clearing Service
126 RRBs Regional Rural Banks
127 RS Regulatory Sandbox
128 R TGS Real Time Gross Settlement
129 SAR System Audit Report
130 SEBI Securities and Exchange Board of India
131 SFMS Structured Financial Messaging System
Payment and Settlement Systems in India | 125
Sl No Acronym Exp ansion
132 SGL Subsidiary General Ledger
133 SIPS Systemically Important Payment System
134 SMS Short Message Service
135 SOF SWIFT Oversight Forum
136 SPC SAARC Payment s Council
137 SRO Self Regulatory Organisation
138 SSS Securities Settlement System
139 STP Straight Through Processing
140 SURU Semi-Urban and Rural
141 SWIFT Society for Worldwide Interbank Financial
Telecommunication
142 TAT Turn-Around Time
143 TPA Third Party Applications
144 TPAP Third Party Application Provider
145 TR Trade Repository
146 TRAI Telecom Regulatory Authority of India
147 TReDS Trade Receivables Discounting System
148 TREPS Tri Party Repo Dealing System
149 TSP Technology Service Provider
150 UIDAI Unique Identification Authority of India
151 UPI Unified Payments Interface
152 UPId Unique Product Identifer
153 USSD Unstructured Supplementary Services Data
154 UTI Unique Transaction Identifier
155 VC Virtual Currency
156 WLA White Label ATM
157 WLAO White Label ATM Operator
Appendix 4
References
1) Benchmarking India's Payment Systems - RBI
2) Assessment of the Progress of Digitisation from Cash to Electronic -
RBI
3) CPMI Red Book
126
| Payment and Settlement Systems in India
NOTES
NOTES
..
RESERVE BANK OF INDIA
DEPARTMENT OF PAYMENT AND SETTLEMENT SYSTEMS
CENTRAL OFFICE
MUMBAI

