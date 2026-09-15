---
id: finance/payments/sepa/epc-sepa-credit-transfer-sct-rulebook-2023
canonical_question: What are the rules, participant obligations, and cycle workflows
  of SEPA Credit Transfer (SCT)?
aliases:
- EPC SCT Rulebook 2023
- SEPA Credit Transfer business rules
- SCT cycle D to D+1
- EPC125-05 standard
- SEPA participant rights and obligations
entity_type: scheme_rulebook
domain: finance > payments > sepa
last_verified: '2026-09-15'
---

# EPC SEPA Credit Transfer (SCT) Scheme Rulebook 2023

## 1. Overview & Executive Summary

SEPA Credit Transfer
0.1.1.1 Scheme Rulebook
www.epc-cep.eu 1 / 102
European Payments Council AISBL
Cours Saint-Michel, 30 - B - 1040 Brussels
T +32 2 733 35 33
Entreprise N°0873.268.927
secretariat@epc-cep.eu
EPC125-05
SEPA Credit Transfer
Scheme Rulebook
EPC125-05 / 2023 Version 1.0 / Date issued: 25 May 2022 / Date effective: 19 November 2023
Public
© 2022 Copyright European Payments Council (EPC) AISBL
Reproduction for non-commercial purposes is authorised, with acknowledgement of the source
SEPA Credit Transfer
Scheme Rulebook
www.epc-cep.eu   2
European Payments Council AISBL
Cours Saint-Michel, 30 - B - 1040 Brussels
T +32 2 733 35 33
Entreprise N°0873.268.927
secretariat@epc-cep.eu
EPC125-05
2023 Version 1.0
Date issued: 25 May 2022
Date effective: 19 November 2023
Table of Contents
0 Document Information 6
0.1 References 6
0.1.1 Defined Terms 7
0.2 Change History 7
0.3 Purpose of Document 11
0.4 About the EPC 12
0.5 Other Related Documents 12
0.5.1 SEPA Credit Transfer Scheme Implementation Guidelines 12
0.5.2 SEPA Credit Transfer Adherence Agreement 13
0.5.3 Rules specific to Extended Remittance Information (ERI) Option 13
1 Vision and Objectives 14
1.1 Vision 14
1.2 Objectives 14
1.3 Commercial Context for Users and Providers of Payment Services 15
1.4 Binding Nature of the Rulebook 16
1.5 Separation of the Scheme from Infrastructure 16
1.6 Other Features of the Scheme 16
1.7 The Business Benefits of the Scheme 17
1.8 Common Legal Framework 18
2 Scope of the Scheme 19
2.1 Application to SEPA 19
2.2 Description of Scope of the Scheme 19
2.3 Additional Optional Services 19
2.4 Currency 20
2.5 Value Limits 20
2.6 Reachability 20
2.7 Remittance Data ‘=> ERI’ 20
3 Roles of the Scheme Actors 22
3.1 Actors 22
3.2 The Four Corner Model 23
www.epc-cep.eu 3
SEPA Credit Transfer Scheme Rulebook 2023 Version 1.0
Date issued: 25 May 2022
3.3 Clearing and Settlement Mechanisms 24
3.4 Intermediary PSPs 24
3.5 Governing laws 24
3.6 Relationship with Payment Service Users 24
4 Business and Operational Model 25
4.1 Naming Conventions 25
4.2 Overview of the SEPA Credit Transfer Process & Time Cycle 25
4.2.1 Commencement of the Execution Time Cycle (Day “D”) 25
4.2.2 Cut-off Times 25
4.2.3 Maximum Execution Time 26
4.2.4 Charging Principles 26
4.3 SEPA Credit Transfer Processing Flow 27
4.3.1 SEPA Credit Transfer Processing Flow 27
4.3.2 Exception Processing Flow 28
4.4 Inquiry process 37
4.4.1 SCT inquiry 37
4.4.2 Response-to-SCT-inquiry 38
4.4.3 Schematic workflo

---

## 2. Core Operational & Technical Architecture

between Participants
Each Participant that is not subject to the Payment Services Directive under its national law shall
vis-à-vis other Participants and vis-à-vis its Payment Service Users and to the extent permitted by
the national law applicable to such Participant, comply with and perform obligations that are
www.epc-cep.eu 78
SEPA Credit Transfer Scheme Rulebook 2023 Version 1.0
Date issued: 25 May 2022
substantially equivalent to those provisions in Title III and IV of the Payment Services Directive
which are relevant for SEPA Credit Transfers.
Further, each Participant (whether or not subject to the Payment Services Directive) shall refrain,
to the extent reasonably possible, from exercising any rights accorded to it under its national law
vis-à-vis other Participants and vis-à-vis its Payment Service Users that either conflict or that could
potentially conflict with the provisions in Title III and IV of the Payment Services Directive.
The obligations of each Participant (whether or not subject to the Payment Services Directive)
under the Rulebook shall apply notwithstanding that the Payment Services Directive is limited in
its geographical scope (art.2 Payment Service Directive). For the avoidance of doubt and
notwithstanding the above paragraphs of this section, it is recognised that the compliance
obligations for a Participant that is not subject to the Payment Services Directive under its national
law and is operating outside the EEA shall not include the obligations resulting from Article 66 and
related Articles of the Payment Services Directive as these Articles should only apply in
combination with the authorisation framework within the EEA in accordance with Titles I and II of
the Payment Services Directive.
The above principles apply mutatis mutandis to each Participant with respect to the provisions of
Article 5 and the Annex of the SEPA Regulation.
www.epc-cep.eu 79
SEPA Credit Transfer Scheme Rulebook 2023 Version 1.0
Date issued: 25 May 2022
6 SEPA Scheme Management
The Scheme Management Entity is EPC AISBL acting in accordance with the EPC By-Laws.
SEPA Scheme Management comprises two functions. The first function involves the administration
of the Schemes and the process of maintaining and managing the evolution of the Schemes, and
the second function involves ensuring compliance with their rules. The detailed rules that describe
the operation of these functions are set out in the Internal Rules of SEPA Scheme Management
under ANNEX II of the Rulebook and in the Dispute Resolution Committee (DRC) Mandate.
6.1 Development and Evolution
The administration, maintenance and evolution function of SEPA Scheme Management establishes
rules and procedures for administering the adherence process for each of the Schemes, as well as
formal change management procedures for the Scheme. The change management procedures aim
to ensure that the Scheme is kept relevant for its users and up-to-date, with structured processes
for initiating and implementing changes to the Scheme, the Rulebook and related documentation.
An important component of change management is the innovation of ideas for enhancing the
quality of the existing Scheme as well for developing new schemes, based always on sound
business cases.
The development of change proposals is to be carried out through clear, transparent and
structured channels, which take into account the views of Participants, SEPA service suppliers,
end-users as well as other concerned groups.
The administration function of the Payment Schemes shall be carried out by the Secretariat, under
the authority of the PSMB.
The development and evolution function shall be performed by the PSMB, supported by the
Payment Scheme Evolution and Maintenance Working Group ("PSEMWG") or by such other
working and support group as the PSMB may designate. The PSMB and the PSEMWG shall perform
the development and evolution function in accordance with the procedures set out in the Internal
Rules.
6.2 Compl

---

## 3. Specifications, Standards & Lifecycle Operations

rticipants at a future date may be pre-published, and a date designated and published when
they will become ERI Option Participants.
In consideration of the mutual obligations constituted by the Rulebook, an applicant agrees to be
bound by, becomes subject to and shall enjoy the benefits of the Annex V of the Rulebook upon
becoming an ERI Option Participant.
5.6 SEPA Credit Transfer Scheme List of Participants
(Addition at the end of the section)
Above-mentioned stipulations also apply on the Sub-List of ERI Option Participants which the EPC
publicly discloses on a regular basis.
5.7 Obligations of an Originator PSP
(Addition at the end of the first list of bullet points)
27) Comply with applicable provisions issued from time to time in relation to Extended Remittance
Information as set out in the Rulebook and Annex V;
Annex V to SEPA Credit Transfer Scheme Rulebook  2023 version 1.0
Date issued: 25 May 2022
5.8 Obligations of a Beneficiary PSP
(Addition at the end of the first list of bullet points)
21) Comply with applicable provisions issued from time to time in relation to Extended Remittance
Information as set out in the Rulebook and Annex V;
5.11 Termination
(Additions at the end of the section)
A Participant may terminate its status as an ERI Option Participant by giving no less than six
months' prior written notice to the Secretariat, such notice to take effect on a designated day (for
which purpose such a day will be designated at least one day for each month).  As soon as
reasonably practicable after receipt of such notice, it or a summary shall be published to all other
Participants in an appropriate manner.
Notwithstanding the previous paragraph, upon receipt of the Participant’s notice of termination as
an ERI Option Participant by the Secretariat, the Participant and the Secretariat may mutually
agree for the termination to take effect on any day prior to the relevant designated day.
An ERI Option Participant shall continue to be subject to the Rulebook in respect of all activities
which were conducted prior to termination of its status as an ERI Option Participant and which
were subject to the Rulebook, until the date on which all obligations to which it was subject under
the Rulebook prior to termination have been satisfied.
Upon termination of its status as an ERI Option Participant, an undertaking shall not incur any new
obligations under the Rulebook.  Further, upon such termination, the remaining ERI Option
Participants shall not incur any new obligations under the Rulebook in respect of such
undertaking's prior status as an ERI Option Participant.  In particular, no new SEPA Credit Transfer
obligations may be incurred by the former ERI Option Participant or in favour of the former ERI
Option Participant.
The effective date of termination of a Participant's status as an ERI Option Participant is (where
the Participant has given notice in accordance with the seventh paragraph of section 5.11) the
effective date of such notice, or (in any other case) the date on which the Participant's name is
deleted from the Sub-List of ERI Option Participants, and as of that date the ERI Option
Participant’s rights and obligations under the Rulebook shall cease to have effect except as stated
in this section 5.11.
This section, sections 5.9, 5.10, 5.12 and Annex II of the Rulebook shall continue to be enforceable
against an ERI Option Participant, notwithstanding termination of such Participant’s status as an
ERI Option Participant.

