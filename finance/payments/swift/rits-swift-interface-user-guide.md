---
id: finance/payments/swift/rits-swift-interface-user-guide
canonical_question: How does a central bank RTGS system interface with SWIFT messaging
  (RITS/SWIFT)?
aliases:
- RITS SWIFT interface
- RTGS SWIFT messaging
- central bank settlement SWIFT
- MT103 MT202 RITS
- FIN-copy payment flow
entity_type: technical_standard_guide
domain: finance > payments > swift
last_verified: '2026-09-15'
---

# RITS SWIFT Interface Architecture: High-Value Settlement and Messaging

## 1. Overview & Executive Summary

RESERVE BANK INFORMATION AND
TRANSFER SYSTEM
RITS/SWIFT
Interface User Guide
May 2022
May 20223
Table of Contents
1. OVERVIEW ...................................................................................................... 5
1.1 Document purpose..................................................................................... 5
1.2 Related documents .................................................................................... 6
1.3 Methods of access to RITS via SWIFT ........................................................... 6
1.4 SWIFT message validations in RITS.............................................................. 6
1.5 BICs - Bank Identifier Codes ....................................................................... 9
1.6 RITS session times................................................................................... 10
1.7 System Queue processing ......................................................................... 11
2. MESSAGE CONTENT SPECIFICATIONS – SWIFT MT OVERVIEW ..................... 12
2.1 Message Structure Overview ..................................................................... 12
3. MESSAGE CONTENT SPECIFICATIONS – ISO 20022 OVERVIEW .................... 17
3.1 Message Structure Overview ..................................................................... 17
4. AUTOMATED INFORMATION FACILITY (AIF)................................................. 22
4.1 RITS online functions used to set up AIF messages....................................... 23
4.2 Pre-and Post-Settlement Advices ............................................................... 24
4.3 Request to receive unsolicited advices ........................................................ 25
4.4 System Queue status values...................................................................... 26
4.5 Credit and liquidity management................................................................ 26
5. AIF - COMMANDS .......................................................................................... 29
5.1 Recalling payments .................................................................................. 29
5.2 Change ESA Status .................................................................................. 32
5.3 Change Credit Status................................................................................ 33
5.4 Change ESA and Credit Status ................................................................... 36
5.5 General Reject

---

## 2. Core Operational & Technical Architecture

be present
in the account number line of field 57 (Account with Institution).
If a payment is being returned because it was recalled by the sender, field 72 (Sender to
Receiver Information) must be present, and should contain the codeword “/RETN/” plus
codes as specified in the SWIFT User Handbook.
If a payment is being returned because it was rejected by the receiver, field 72 (Sender to
Receiver Information) must be present, and should contain the codeword “/REJT/” plus
codes as specified in the SWIFT User Handbook.
Unpublished BICs are not to be used within the Text Block of the payment instruction. An
unpublished BIC is a BIC used within the PDS which has been designated by SWIFT as not
to be published in the SWIFT BIC Directory.
8.2.2 Single Customer Credit Transfer (MT103STP)
Tag Field Name SWIFT
M/O
PDS
M/O
Notes
MT103STP
Basic Header Block Contains sender’s SWIFT address and other
data
RITS/SWIFT Interface User Guide
SWIFT Payment and Related Messages (SWIFT MT CUG)
May 202278
Tag Field Name SWIFT
M/O
PDS
M/O
Notes
Application Header Block –
Input
Contains receiver’s SWIFT address and
other data
User Header Block
Block Identifier M M “3”
103 Service Code O M
113 Banking Priority O O
108 Message User Reference O O
119 Validation Flag M M “STP”
Message Text
Block Identifier M M “4”
20 Transaction Reference
Number
M M
13C Time Indication O O
23B Bank Operation Code M M
23E Instruction Code O O
26T Transaction Type Code O O This field should not be used
32A Value Date, Currency Code,
Amount
M M
33B Currency Instructed Amount O O
36 Exchange Rate O O
50a Ordering Customer M M
52a Ordering Institution O O
53a Sender’s Correspondent O O
54A Receiver’s Correspondent O O This field should not be used
55A Third Reimbursement
Institution
O O This field should not be used
56A Intermediary O O
57A Account with Institution O M
59a Beneficiary Customer M M
70 Details of Payment Order O O
71A Details of Charges M M
71F Sender’s Charges O O
71G Receiver’s Charges O O
72 Sender to Receiver
Information
O O
RITS/SWIFT Interface User Guide
SWIFT Payment and Related Messages (SWIFT MT CUG)
May 202279
Tag Field Name SWIFT
M/O
PDS
M/O
Notes
77B Regulatory Reporting O O
N.B. A BSB code, preceded by “//AU”, must be present in the account number line of the
first of fields 56 (Intermediary) or 57 (Account with Institution) to appear in the payment
instruction. See the Conditional Field Rules which follow.
CONDITIONAL FIELD RULES
If field 53 (Sender’s Correspondent) is present, it must be in the format 53A and must
contain the RITS/RTGS BIC (i.e. RSBKAUYY for the live RTGS environment and RSBKAUY0
for the test and training environment).
If field 56 (Intermediary) is present, a BSB code, preceded by “//AU”, must be present in
the account number line of this field.
If field 56 (Intermediary) is not present, a BSB code, preceded by “//AU”, must be present
in the account number line of field 57 (Account with Institution).
If a payment is being returned because it was recalled by the sender, field 72 (Sender to
Receiver Information) must be present, and should contain the codeword “/RETN/” plus
codes as specified in the SWIFT User Handbook. When returning an MT103STP message
the message will be returned as an MT103 (ie the validation flag field (tag 119) should not
be used for a returned message).
If a payment is being returned because it was rejected by the receiver, field 72 (Sender to
Receiver Information) must be present, and should contain the codeword “/REJT/” plus
codes as specified in the SWIFT User Handbook. When rejecting an MT103STP it is to be
rejected as an MT103 (ie the validation flag field (tag 119) should not be used for rejecting
a message).
Unpublished BICs are not to be used within the Text Block of the payment instruction. An
unpublished BIC is a BIC used within the PDS which has been designated by SWIFT as not
to be published in the SWIFT BIC Directory.
8.2.3 General Financial Institution Transfer (MT202)
Tag Field Name

---

## 3. Specifications, Standards & Lifecycle Operations

ed for the exchange of SWIFT
Payments between banks’ Gateways (SWIFT CBTs) and the CSI.
SWIFTNet Copy Service
over InterAct
SWIFTNet Copy service is the name of the service provided by SWIFT and
used for the ISO 20022 CUG of the SWIFT PDS.
RITS/SWIFT Interface User Guide
Glossary
May 2022157
SWIFT Payment A SWIFT Payment is a one-sided payment, sent via the SWIFT FIN-Copy
service or SWIFTNet Copy service over InterAct, to be applied against
ESAs (in RITS) upon settlement. SWIFT Payments include customer
details which are removed by the SWIFT FIN-Copy service or SWIFTNet
Copy service over InterAct, with only interbank settlement details passed
to RITS for settlement testing.
SWIFT PDS The SWIFT Payment Delivery System is a closed user group of ESA
holders for sending SWIFT Payments to RITS via the SWIFT FIN-Copy
service or SWIFTNet Copy service over InterAct. AusPayNet conducts the
SWIFT PDS.
SWIFT PDS ISO 20022
Closed User Group
(CUG)
The closed user group of RITS members that participate in the High Value
Clearing System (HVCS) and use the SWIFTNet Copy service over
InterAct in Y mode for exchanging payments in an ISO 20022 format.
SWIFT PDS MT/SWIFT
MT Closed User Group
(CUG)
The closed user group of RITS members that participate in the High Value
Clearing System (HVCS) and use the SWIFT FIN-Copy service in Y mode
for exchanging payments in a SWIFT MT format.
SWIFT Alliance Access SWIFT Alliance Access is the messaging software that allows users to
connect their in-house applications with the SWIFT Network.
SWIFT Alliance Gateway SWIFT Alliance Gateway acts as a communication interface between the
SWIFT Network and message software such as SWIFT Alliance Access.
System The "System" refers to RITS.
System Administrator The RBA is the System Administrator and is responsible for oversight of
the System, including such matters as establishing members, allocating
passwords and System functions to member institutions, setting opening
and closing times etc.
System Queue The System Queue in RITS in which all transactions are tested to ensure
that Paying Members have sufficient funds.
Transaction ID Unique ID assigned to a transaction within RITS. For SWIFT Payments,
this is the TRN (field 20).
Transaction Processing
Status
Indicates the Status of a Payment, i.e. Entered, Verified, Sent, Received
etc.
Transaction Reference
Number (TRN)
Unique ID assigned by the sender to messages sent over the SWIFT
network. The TRN is also used as the Transaction ID within RITS for
SWIFT Payments (field 20).
Transaction Type A Transaction Type is an abbreviated description of a transaction used in
reports and enquiry functions.
Transaction(s), or
payment(s)
Value transactions affecting Cash Accounts and/or ESAs.
Unsecured Cash Limit The amount (if any) by which a Participating Bank has authorised its
Participant’s Cash Account to go into debit.
Unsettled Advice Unsettled Advices are sent to Paying Banks’ Gateways and list any
unsettled Payments that remain in the System Queue at Close of Day.
Unsettled Transaction Transactions that are on the System Queue at the end of the RITS day,
and have not been settled.
Unsolicited Advices Message-based Advices created by RITS, and sent to banks as required.
Members must make a once-off selection to receive these Advices.
Warehoused
Transactions
Transactions entered into RITS ahead of the settlement date. RITS allows
for up to 5 business days ahead of settlement date.
RITS/SWIFT Interface User Guide
Glossary
May 2022158

