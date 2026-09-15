---
id: finance/payments/iso-20022/iso-20022-corporate-actions-lifecycle
canonical_question: How are corporate actions and reorganizations structured in ISO
  20022 messaging?
aliases:
- ISO 20022 corporate actions
- seev.031 seev.034 seev.035 messaging
- corporate reorganization lifecycle
- DTCC ISO 20022 user guide
- entitlements and allocations ISO 20022
entity_type: technical_standard_guide
domain: finance > payments > iso-20022
last_verified: '2026-09-15'
---

# ISO 20022 Messaging for Corporate Actions: Lifecycle, Entitlements and Allocations

## 1. Overview & Executive Summary

DTC CORPORATE ACTIONS
USER GUIDE:
ISO 20022 MESSAGING FOR REORGANIZATIONS
ENTITLEMENTS AND ALLOCATIONS
VERSION 1.3
MARCH 09, 2021
© 2021 DTCC. All rights reserved.  DTCC, DTCC (Stylized), ADVANCING FINANCIAL MARKETS. TOGETHER, and the
Interlocker graphic are registered and unregistered trademarks of The Depository Trust & Clearing Corporation.
The services described herein are provided under the “DTCC” brand name by  certain affiliates of The Depository Trust &
Clearing Corporation (“DTCC”).  DTCC itself does not provide such services.  Each of these affiliates is a separate legal
entity, subject to the laws and regulations of the particular country or countries in wh ich such entity operates. Please see
www.dtcc.com  for more information on DTCC, its affiliates and the services they offer.
This guide is meant as an educational tool to assist in your understanding of ISO 20022 messaging as it relates to
corporate action processing at DTCC. It should not be used as a basis for systems applications coding. For coding
purposes, please refer to specific schemas and message implementation guides that can be found at
https://www.dtcc.com/settlement- and-asset-services/corporate-actions -pr ocessing/iso-20022-messaging- specifications .
Doc Info: March 09, 2021
Publication Code:  CA222
Service: DTC Corporate Actions
Title: ISO 20022 Messaging for Reorganizations : Entitlements and Allocations
Contents
ISO 20022 Messaging for Reorganiz ations: Entitlem ents and All ocati ons 3
TABLE OF CONTENTS
An Introduction to ISO 20022 Messaging ................................................................................... 8
What is ISO 20022 Messaging? ................................................................................................. 8
Benefits of Using ISO 20022 Messaging for Corporate Actions .......................................................8
Benefits of Using ISO 20022 for Reorganizations Processing ........................................................9
How Can I Learn More? ............................................................................................................9
Data Dictionaries, Scenarios, Message Usage Guidelines, and Event Templates .........................11
Data Dictionaries and Applicability to Reorganization Events ........................................................ 11
Announcements Data Dictionary ............................................................................................. 12
Using the Events

---

## 2. Core Operational & Technical Architecture

e.
The NEWM generation date and REPL message period for the CANO-E varies according to event type.
The following subsections list the eligible balances and provide tables explaining the message periods for
mandatory and voluntary events.
Mandatory Events
CANO-E Messaging Period for Mandatory Events
The eligible balance for mandatory events is determined by the following:
• For Partial Mandatory Puts, you have position in the contra CUSIP regular unpledged (“free”)
account.
• For all other mandatory events, you have position in the event CUSIP in one of the following
accounts:
o 10: Regular Unpledged account.
o 11: Regular Paid account.
o 14: Regular Pledged account.
o 18: Investment Regular Pledged account.
o 22: Investment Regular Unpledged account.
o 26: Call with Interest account.
o 28: Call No Interest account.
o 40: Withdrawal by Transfer account.
o Position Memo Segregation account.
CANO-E Messages
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 63
The final column in the following table specifies the balance that triggers each event type.
See the Reorg Events Using CANO-Es mapping document for full event type information.
ACTIVITY
CODE
CA WEB
EVENT TYPE
CAEV CODE /
SUB EVENT TYPE
CANO-E MESSAGE
START / END DATE
MESSAGE
TRIGGER
61
Redemptions
of Warrants
REDM BEGINS: Payment Date – 7
ENDS: Payment Date
Event
Security
balance
65
Mandatory Put
(No Retain)
BPUT BEGINS: Payment Date – 7
ENDS: Payment Date
Event
Security
balance
65G
Mandatory Put
(Book Entry)
BPUT BEGINS: Payment Date – 7
ENDS: Payment Date
Event
Security
balance
65P
Partial
Mandatory Put
BPUT BEGINS: Payment Date – 7
ENDS: Payment Date
Contra
CUSIP
balance
69
Full Call MCAL BEGINS: Payment Date – 7
ENDS: Payment Date
Event
Security
balance
71
Merger
(Securities)
MRGR / SECU BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS:  Payment Date (DTC Anticipated
Payment Date)
Event
Security
balance
72
Merger (Cash)  MRGR / CASH BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS: Payment Date(DTC Anticipated
Payment Date)
Event
Security
balance
73
Reverse Stock
Split
SPLR BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS: Payment Date (DTC Anticipated
Payment Date)
Event
Security
balance
79
Liquidation
(Presentation
Required)
LIQU / PREQ BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS: Payment Date (DTC Anticipated
Payment Date)
Event
Security
balance
90
Merger (Cash
and
Securities)
MRGR / CASE BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS: Payment Date (DTC Anticipated
Payment Date)
Event
Security
balance
CANO-E Messages
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 64
93
Various  • PLAC
• CHAN
• CHAN / PREQ
• CONV
• EXOF
• EXOF / ADRS
(TMTN)
• EXOF / ADRS
(TMTN)
• EXRI
• LIQU / PREQ
• MRGR
• OTHR
• REDM / SECU
• SPLF / PREQ
• SPLR
• WRTH
BEGINS: Payment Date (DTC Anticipated
Payment Date) – 1
ENDS: Payment Date (DTC Anticipated
Payment Date)
Event
Security
balance
CANO-E Daily Messaging Times for Mandatory Events
Messages for mandatory events are sent daily at 8:00 p.m. during the range specified above.
Voluntary Events
CANO-E Messaging Period for Voluntary Events
For voluntary events, the messaging period is the widest relevant period for the individual reorganization
event type and could include early response deadlines and cover protect periods. The CANO-E message
is sent during this period when you have any position (eligible or non-eligible) in this event.
ACTIVITY
CODE
CA WEB
EVENT TYPE
CAEV CODE /
SUB EVENT TYPE
CANO-E MESSAGE
START / END DATE
MESSAGE
TRIGGER
52
Various  • BIDS
• BIDS / BTST
• BIDS / CASE
• BIDS / COTE
• BIDS / SETE
• BPUT
• CONS / WITH
• CONS / WITO
BEGINS earliest of:
Early Response Deadline – 7
or
Action Period Start Date – 7
ENDS latest of:
Expiry Date
or
Cover Expiration Date
Event
Security
balance
CANO-E Messages
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 65
ACTIVITY
CODE
CA WEB
EVENT TYPE
CAE

---

## 3. Specifications, Standards & Lifecycle Operations

Partial Mandatory Put
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 123
Scenario 14: Optional Put
Activity Codes: 58, 58B.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 14a: Optional Put (1 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 124
Scenario 14b: Optional Put (2 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 125
Scenario 15: Put (Mortgage-Backed)
Activity Codes: 62, 62B.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 15a: Mortgage-Backed Put (1 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 126
Scenario 15b: Mortgage-Backed Put (2 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 127
Scenario 16: Mandatory Put for Cash with Right to Retain
Activity Code: 65B.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 16a: Mandatory Put for Cash with Right to Retain (1 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 128
Scenario 16b: Mandatory Put for Cash with Right to Retain (2 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 129
Scenario 17: Mandatory Put for Securities with Right to Retain
(Put Extendable)
Activity Codes: 65R.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 17a: Mandatory Put for Securities with Right to Retain (1 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 130
Scenario 17b: Mandatory Put for Securities with Right to Retain (2 of 2)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 131
Scenario 18: Rights Subscription
Activity Code: 59.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 18a: Rights Subscription (1 of 3)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 132
Scenario 18b: Rights Subscription (2 of 3)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 133
Scenario 18c: Rights Subscription (3 of 3)
Appendix A: Messaging Scenar ios for Reorganization Events
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 134
Scenario 19: CD Early Redemptions and Survivor Options (“Death
Puts”)
Activity Codes: 53 and 66P.
See the Reorganization Event Codes table for a list of ISO 20022 event codes.
Scenario 19: CD Early Redemptions / Survivor Options
ISO 20022 M essagi ng for Reor ganiz ations: Entitlements and Allocations 135
FOR MORE INFORMATION
Email DTCC Learning at:
corelearning@dtcc.com
or visit us on the web at:
www.dtcclearning.com
FOR MORE INFORMATION
Email DTCC Learning at:
corelearning@dtcc.com
or visit us on the web at:
www.dtcclearning.com

