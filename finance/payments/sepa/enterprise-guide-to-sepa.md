---
id: finance/payments/sepa/enterprise-guide-to-sepa
canonical_question: What is the complete overview of SEPA instruments (SCT, SDD, SCT
  Inst) and EU payment regulation?
aliases:
- SEPA comprehensive guide
- SEPA Direct Debit vs Credit Transfer
- SCT Inst instant payments
- IBAN and BIC in SEPA
- SEPA cross-border clearing
entity_type: comprehensive_guide
domain: finance > payments > sepa
last_verified: '2026-09-15'
---

# Enterprise Guide to SEPA: Instruments, Regulations, and Instant Payments

## 1. Overview & Executive Summary

SEPA Guide
October 2021
Executive Summary
Developed by the European Payments Council (‘EPC’), the
Single Euro Payments Area (‘SEPA’) expands on the vision
behind the Euro to establish a single monetary and
economic union.
Specifically, SEPA is geared toward creating a borderless
system of Euro payments throughout SEPA countries and
territories by putting a consistent set of standards, rules and
conditions in place. The ultimate goal is to make sending and
receiving SEPA zone payments as easy and cost effective as
non-urgent domestic payments.
The adoption by EU of Payment Services Directive 1 & 2 in
2007 and 2015 also facilitated this objective as it established
the legal foundation for the payments within European Union.
In 2021, the geographical scope of the SEPA schemes covers
36 countries and territories including the 27 EU Member
States of European Union plus Iceland, Norway, Liechtenstein,
Switzerland, Monaco, San Marino, Andorra, Vatican City State/
Holy See and UK.
The SEPA zone brings numerous benefits to the corporates:
® SEPA Credit Transfer (‘SCT’) is a harmonised payment
method for both cross-border and domestic Euro
payments within the SEPA zone. It allows the Originator to
have full control over the delivery of the funds and gives the
assurance that the payment is made in full to
the Beneficiary;
® SEPA Credit Transfer Instant (‘SCT Inst’) is a pan-European
payment method launched in 2017. It allows the Beneficiary
to immediately get the funds and reuse them. Payments will
be made within 10 seconds to the Beneficiary;
® SEPA Direct Debit allows the corporates to collect the funds
on an agreed future date. There are 2 schemes, B2B and
CORE in SEPA zone;
® The Usage of XML ISO 20022 increases the standardisation
of Payment processes and saves time and money during the
implementation of Payment Treasury solutions in Europe.
Then, XML based payment factory is a real benefit for the
construction PAN European POBO & COBO structures; the
reconciliation is simplified by standardised items forwarded
without alteration to the Beneficiary and reflected in the
account statements.
We’ve created ‘Your Guide to SEPA’ to provide you with
concise, expert knowledge on the key SEPA characteristics
and benefits of harnessing the full potential of SEPA and
ISO 20022 XML. In the pages that follow, you’ll benefit from
the experience we’ve gained as we’ve helped a number of
companies across the entire SEPA zone transition from their
legacy systems to SEPA and assis

---

## 2. Core Operational & Technical Architecture

e Debtor;
® The Debtor signs the Mandate and sends it back;
® The Debtor can cancel the Mandate at any time; if the
Debtor does not cancel the Mandate, it automatically expires
36 months after the last collected Direct Debit; and
® The Creditor should check the validity of the Mandate in
advance of submitting a SEPA Direct Debit. Using an invalid
Mandate would lead to an unauthorised Direct Debit.
Storage of the Mandate
The signed Mandate, whether it be paper-based or electronic,
must be stored by the Creditor for as long as the Mandate
exists and for the period of its possible dispute.
Signed SEPA mandate
Settlement D
Pre-notiﬁcation
(D-14 or as agreed)
ContractTerms and
conditions
of accounts
Direct Debit
advice/
statement
entry
B2B:
Mandate
Check
Presentation
Core: D-1
B2B D-1
Initiation *
Core D-1
B2B D-1
Credit
Entry
2
3 7b0 7a 0
1
6
5 4
Debtor Creditor
Debtor
Bank
Creditor
Bank
SEPA Guide
8
The Creditor is responsible for maintaining the Mandate, as well
as its history. The Creditor must be able to present a copy of
the Mandate to the Debtor’s Bank upon request. If the Creditor
isn’t able to do so, a refund and compensation will be required
if the Debtor objects to the debit.
Please note that:
® SDD B2B collections can only be executed once a signed
Mandate is registered by Debtor Banks.
® SDD CORE collections is done without a Bank’s validation of
the validity of the Mandate but can be refunded without any
reason during 8 weeks for an authorised Mandate.
SEPA Direct Debit Mandate attributes
Mandatory attributes:
® Unique Mandate reference
® Name of the Debtor
® Address of the Debtor (mandatory when the Creditor
Bank or the Debtor Bank is located in a non-EEA SEPA
country or territory)
® Postal code/city of the Debtor
® Debtor’s country of residence
® Debtor’s account number (IBAN)
® The BIC code of the Debtor Bank*
® Creditor company name
® Creditor’s identifier
® Creditor’s address street and number
® Creditor’s postal code and city
® Country of the Creditor
® Type of payment (only the value ‘one-off’
and ‘recurrent are allowed)
® Signature place and time
® Signature(s) of the Debtor(s)
* The delivery of the BIC of the Debtor Bank in SDD collections
is optional when both the Creditor Bank and the Debtor Bank
are based in a country of the European Economic Area (EEA).
The provision of the BIC of the Debtor Bank in SDD collections
remains mandatory when the Creditor Bank or the Debtor Bank
is in a non-EEA SEPA country.
Mandate Reference
Every SEPA Direct Debit Mandate must have a unique Mandate
reference, also referred to as a Mandate ID or ‘UMR’. This
reference is assigned by the Creditor and enables the Debtor
to clearly identify the Mandate in connection with the creditor
ID. The Debtor can therefore automatically check whether
incoming direct debits are permitted.
When assigning the Mandate reference, using existing
customer or contract numbers, expanded by one number or
date value, is typically the easiest. A Mandate reference can be
up to 35 characters long, and include any combination of the
following:
® A–Z
® a–z
® 0 –9
® + ?/ \ : ( ) . , ‘
® Blank spaces
The Mandate reference in combination with the identifier of the
Creditor (without the extension, called Creditor Business Code)
must be unique for each Mandate
Creditor Reference/Creditor Identifier
The Creditor Identifier is unique in the SDD Scheme, it allows
to identify a legal entity, or an association that is not a legal
entity, or a person assuming the role of the Creditor.
A Creditor may use more than one Identifier*; for example, if the
client needs to have local (on country level) identification for
their customers. In parallel, the same creditor identifier can be
used in different SEPA countries.
Likewise, a Creditor may use the ‘Creditor Business Code’
extension to identify different business activities. As a reminder,
the Creditor may use the same Creditor Identifier for both the
SDD CORE & B2B Schemes.
Example of Creditor Identiﬁer
National identife

---

## 3. Specifications, Standards & Lifecycle Operations

d with a network
of offices across Europe with extensive payments capabilities
– giving us the ability to provide a coordinated delivery of SEPA
compliant transactions.
When you choose HSBC, you’ll have access to a dedicated
team of SEPA experts who will work with you through SEPA
implementation at the country, regional and global level to:
® keep you informed on the latest SEPA market news and talk
to you about what this means for your business;
® advise you on technical and strategic aspects of SEPA
End Date Regulation, including how best to go about
implementing ISO 20022 XML;
® help manage and centralise payments from many locations
across Europe, assisting you in your rationalisation and
treasury transformation project; and
® provide you with insights about niche products, market
practices or local restrictions to be taken into account when
rationalising.
In addition to this, HSBC is among industry pioneers that
are adopting the ISO 20022 XML messaging in standard
formats to allow clients to integrate core treasury, payables
and receivables applications to share with Banking and other
financial partners.
If you have any questions, please refer to hsbcnet.com/sepa or
contact your HSBC representative. Our SEPA specialists will be
happy to speak with you and provide you guidance to help you
through the SEPA integration.
SEPA Guide
14
Appendix: Useful Links & Contact Information
Useful Links
1) About SEPA: europeanpaymentscouncil.eu/about-sepa
2) Guidelines for the appearance of Mandate: https://www.europeanpaymentscouncil.eu/document-library/guidance-
documents/guidelines-appearance-mandates-sepa-direct-debit-schemes
3) Translation of the SDD Mandate in all SEPA languages
SDD CORE: europeanpaymentscouncil.eu/other/core-sdd-mandate-translations
SDD B2B: europeanpaymentscouncil.eu/other/sepa-b2b-dd-mandate-translations
Contact Information
Find out more about SEPA by visiting our website at: hsbcnet.com/sepa
Alternatively, speak with your usual HSBC representative.
Features and functionality may vary by country. Please confirm availability with your local HSBC Representative.
HSBC Bank endeavours to ensure the information in this document is correct and doesn’t accept any liability for error or omission.
You’re solely responsible for making your own independent appraisal of, and investigations, into the products and services referred
to in this document and you shouldn’t rely on any information in this document as constituting investment advice. This document
does not constitute any form of legal, tax or account advice from HSBC Bank plc to you. HSBC Bank is not responsible for the
content of third-party websites. No part of this publication may be reproduced, stored in a retrieval system, or transmitted, on any
form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the prior written permission of HSBC
Bank plc.
Issued by HSBC Bank plc. We’re a principal member of the HSBC Group, one of the world’s largest Banking and financial services
organisations with around 6,200 offices in 74 countries and territories.
HSBC Continental Europe, Société Anonyme is authorised and regulated by the European Central Bank, by the Autorité de Contrôle
Prudentiel et de Résolution and by the Autorité des Marchés Financiers. HSBC Continental Europe is incorporated in France with
registered office at 38, Avenue Kléber, 75116 Paris, France and Company Register Number 775 670 284.
©HSBC Bank plc 2019. All Rights Reserved.
15

