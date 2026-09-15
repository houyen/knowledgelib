---
id: finance/payments/sepa/formats-for-sepa-credit-transfer-orders
canonical_question: What are the required XML message formats and schemas for SEPA
  payment orders (pain.001)?
aliases:
- SEPA XML payment order format
- pain.001.001.03 format
- EU credit transfer file schema
- SEPA pain.001 non-banks
- ISO 20022 XML payment order
entity_type: technical_specification
domain: finance > payments > sepa
last_verified: '2026-09-15'
---

# Technical Formats for EU and SEPA Credit Transfer Payment Orders

## 1. Overview & Executive Summary

© VTB Bank (Europe) SE – Formats for EU-/ SEPA Credit Transfers - Non Banks                                   Page 1 / 5
VTB Bank (Europe) SE
Rüsterstraße 7–9
60325 Frankfurt
Germany
FORMATS FOR PAYMENT ORDERS
EU-Payments /
SEPA Credit Transfer
for Non-Banks
© VTB Bank (Europe) SE – Formats for EU-/ SEPA Credit Transfers - Non Banks                                   Page 2 / 5
VTB Bank (Europe) SE
Rüsterstraße 7–9
60325 Frankfurt
Germany
Table of contents
Table of contents ................................ ................................ ................................ ................... 2
General ................................ ................................ ................................ ................................ . 3
Definition EU-Payment / SEPA Credit Transfer ................................ ................................ ..... 3
Format-Requirements for the Cash Remittance within the EU ................................ ............... 3
Explanation of Terms................................ ................................ ................................ ............. 4
BIC - Bank Identification Code ................................ ................................ .................... 4
IBAN – International Bank Account Number ................................ ...............................  4
SEPA – Single Euro Payments Area ................................ ................................ ........... 4
Payment Orders in Foreign Currencies ................................ ................................ ....... 5
© VTB Bank (Europe) SE – Formats for EU-/ SEPA Credit Transfers - Non Banks                                   Page 3 / 5
VTB Bank (Europe) SE
Rüsterstraße 7–9
60325 Frankfurt
Germany
General
In order to execute payment orders within the EU community in a cost-effective way, the new
EU regulation on cross border payments provides a cheap handling of EURO payments
within the EU countries.
The basis for a cost-effective execution is a standardised payment order which will
automatically be executed and which does not need any manual input.
Please note: A critical circumstance for a standardised STP execution lies in the registration
requirements that vary from country to country.
Definition EU-Payment / SEPA Credit Transfer
A EU-Payment is a payment order which
 is written in a EURO-Payment Instruction form
 is sent by fax using a copy of EU-Payment Instruction form
 is sent electronically as a SEPA Credit Transfer (XML-Format

---

## 2. Core Operational & Technical Architecture

struction form.
 an IBAN for the beneficiary is given.
 the BIC for all involved banks are given.
 it is to be paid within the EU community.
 the charges option is „SHA“.
© VTB Bank (Europe) SE – Formats for EU-/ SEPA Credit Transfers - Non Banks                                   Page 4 / 5
VTB Bank (Europe) SE
Rüsterstraße 7–9
60325 Frankfurt
Germany
Explanation of Terms
 BIC - Bank Identification Code
The BIC is a bank's unique address in the SWIFT format.
This code consists of 4 characters for the name of the bank, 2 characters for the country, 2
characters for the town and, if applicable, another 3 characters for a branch.
Bank Country Town Branch applicable for
E.g OWHB DE  FF   VTB Bank (Europe) SE, Frankfurt
 IBAN – International Bank Account Number
The IBAN is a globally standardised identifier of a bank account, which is initially to be used
solely in international payment transactions.
The introduction of the IBAN is intended to simplify and speed up the processing of
international payment transactions over the longer term.
The length of the IBAN can vary from country to country. A uniform length of 22 characters
has been agreed for Germany. It is composed of the 2 character country code, the 2
character check digit, the 8 character bank identification code and your 10 character account
number.
The example below is meant to show you how this functions:
Example: Your account number:  0123456789
Our bank identification code: 503 200 00
Your IBAN: DE55 5032 0000 0123 4567 89
 SEPA – Single Euro Payments Area
Abbreviation for Single Euro Payments Area, the European Mass-Payment-System which
allows to settle EURO-Payment between all attending EU-Banks directly
© VTB Bank (Europe) SE – Formats for EU-/ SEPA Credit Transfers - Non Banks                                   Page 5 / 5
VTB Bank (Europe) SE
Rüsterstraße 7–9
60325 Frankfurt
Germany
 Payment Orders in Foreign Currencies
Important note for transactions in currencies other than EUR:
If the beneficiary´s account or the „account with bank“ (Field 57 A) is not kept with VTB Bank
(Europe) SE, the correspondent bank of the beneficiary bank (field 57) must be indicated in
your payment order (US bank for USD, Swiss bank for CHF etc.).
If you are using our MIP product, there are two options to indicate this information:
– Using the BIC of the Correspondent Bank and the Instruction Code in field 72 (S ender to
Receiver Information) there is a "drop -down menu". In this case the Instruction Code /INT/
(Intermediary Bank) is selected and the BIC has been inserted in the adjacent field.
Example:
– Using the BIC of the Correspondent Bank and your instruction in the field (Additional
instructions for bank) for example "Via DEUTUS33" or "/ INT / DEUTUS33".
Example:
We can not take any responsibility for delays resulting from incomplete information regarding
correspondent bank for these payments.

