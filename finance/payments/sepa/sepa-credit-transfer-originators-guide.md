---
id: finance/payments/sepa/sepa-credit-transfer-originators-guide
canonical_question: How do corporate originators submit, validate, and execute SEPA
  payment batches?
aliases:
- SEPA originator guide
- corporate SEPA batch payment
- pain.001 customer credit transfer initiation
- originator validation rules
- SEPA payment calendar
entity_type: implementation_guide
domain: finance > payments > sepa
last_verified: '2026-09-15'
---

# SEPA Credit Transfer (SCT) Originator and Corporate Onboarding Guide

## 1. Overview & Executive Summary

May 2014
SEPA Credit
Transfers
Originators
Guide
May 2014
This document is published by Bank of Ireland, and both it, and its’ contents, are the property
of Bank of Ireland.  This document may not be reproduced or further distributed, in whole or
in part, without the express written permission of Bank of Ireland.
May 2014
Document Purpose ................................................................................................................................................................................................................................. 3
1.0 Credit Transfer Originators - Key Changes & Impacts ................................................................................................................................. 4
2.0 Credit Transfer Originator Migration to SEPA ..................................................................................................................................................... 5
2.1 SEPA XML – New File Format (PAIN001) .................................................................................................................................................. 5
2.2 BIC AND IBAN ......................................................................................................................................................................................................... 5
2.3 SEPA Originator Identification Number ...................................................................................................................................................... 5
3.0 Credit Transfer Submission Timelines ..................................................................................................................................................................... 6
3.1 BATCHING  ................................................................................................................................................................................................................ 6
3.2 PROCESSING DATES ........................................................................................................................................................................................ 6
4.0 Submitting Payment Files under SEPA ................................................................................................................................................................... 7
4.1 OVERVIEW  ..........................................................................

---

## 2. Core Operational & Technical Architecture

r to verify
and authorise the Credit Transfer file.
If you are an existing Business On Line customer, your existing Administrators (also known as Customer User Administrator
or CUA) will automatically be assigned as your administrators for the submission and authorisation of files.
If you are a WINBITS customer, Bank of Ireland will be in touch with you to register your Administrators.
Once your Administrators have been identified and communicated to Bank of Ireland, Bank of Ireland will be in touch with you to
communicate your User ID’s and passwords.
May 2014
fIf the file format is incorrect or incorrectly named:
The file is invalid and cannot be uploaded and transferred to Business On Line Payments Plus. A message pointing to the
invalid file will appear in your inbox on Business On Line File Gateway.
fIf a file fails pre-processing validation (e.g.  number of transactions is incorrect):
The file appears in the File Rejections Report area on Business On Line Payments Plus. The File Rejection Report is a report
which is generated when a PAIN001 file fails pre-processing validation checks.
The following table is a listing of pre-processing validation error messages on SEPA Credit Transfer files. If your file has failed any
of these checks, the File Rejection Report will detail one or more of the following messages:
Reason Text Reason Description
File Error You have exceeded your limit. Please review your file and re-submit or contact your relationship
manager
File Error This is a duplicate file. Please review your file and re-submit
File Error You have included payments with a value date which is more than 60 days in the future, or 30
days in the past. Please review your file and resubmit.
File Error The nominated account number is not registered under this Originator ID or there are
inconsistent Originator IDs present on this file.
File Error The Batch ID on the File is not unique.  Please review your file and resubmit.
File Error The total number of transactions in the file does not match the accumulated number of
transactions for the batch (s).  Please review your file and resubmit.
File Error The accumulated number of transactions in a batch does not match the total number of
transactions for that batch.  Please review your file and resubmit.
File Error The accumulated value of transactions in a batch does not match the total value of
transactions for that batch.   Please review your file and resubmit.
File Error The accumulated value of transactions in a file does not match the total value of transactions
for that file.   Please review your file and resubmit.
File Error An error has occurred with your file.  Please review your file and re-submit.
5.0 Problems with the Credit Transfer File
May 2014
This section describes the Rejections to an Originators account following the submission of a PAIN001 file and subsequent
rejections and returns arising from the submitted transactions.
Under the SEPA scheme originators are debited with the full value of the batch on the Requested Execution Date.
6.1 Settlement
Under SEPA, it is possible to submit a single file with multiple settlement dates and credit account numbers.  For this reason, files
are grouped into batches based on the requested execution date or the debtor account.
The bulk debit applied to the originator account is applied per batch on requested execution date.  For example, if a file
contains three batches, the originator account will receive three separate bulk debits.
Where a batch is submitted with a requested execution date more than 60 days in the future or 30 days in the past, each batch
will be rejected (and reported on the PAIN002).
6.2 Rejections / Returns
A SEPA “r-message” can refer to any one of a number of possible Credit Transfer rejection notifications under SEPA .
R-messages (rejects and returns) can occur either pre-settlement (prior to or on D) or post-settlement (after D).
fRejections (Pre-settlement) include rejections where transactions have f

---

## 3. Specifications, Standards & Lifecycle Operations

evel of the field name tag within the document.
For example:
‘+’ would represent a Parent Element.
‘++’would represent the Child Element of the previous Parent Element
TAG DEPTH TAG STRUCTURE
+ <>
++ <>
<>
+++ <>
<>
<>
++++ <>
<>
<>
<>
May 2014
Appendix 2.6:  Reason Codes
Originators may receive the following reasons codes as part of the PAIN.002.001.03 message to detail the reason for the
rejection. This code will be populated in the code tag, field index 3.23, as outlined in the Transaction Information block in the file
format section of this document.
Post-Settlement Returns/Refunds
Return codes
The following table lists the reason codes that could occur for a return message
ISO Code SEPA Reason as specified in the Rulebook
AC01 Account identifier incorrect (i.e. invalid IBAN)
AC04 Account closed
AC06 Account blocked
Account blocked for direct debit by the Debtor
AG01 Direct debit forbidden on this account for regulatory reasons
AG02 Operation/transaction code incorrect, invalid file format
Usage Rule: To be used to indicate an incorrect ‘operation/transaction’ code
AM04 Insufficient funds
AM05 Duplicate collection
BE05 Identifier of the Creditor incorrect
FF05 Direct Debit type incorrect
MD01 No valid Mandate
MD07 Debtor deceased
MS02 Refusal by the Debtor
MS03 Reason not specified
RC01 Bank identifier incorrect (i.e. invalid BIC)
RR01 Missing Debtor Account Or Identification
RR02 Missing Debtors Name Or Address
RR03 Missing Creditors Name Or Address
RR04 Regulatory Reason
SL01 Specific Service offered by the Debtor Bank
DNOR Debtor bank is not registered under this BIC in the CSM
Refund codes
The following table lists the reason codes that could occur for a refund message from a debtor bank:
ISO Code SEPA Core Reason as specified in the Rulebooks
MD01 Unauthorised transaction
MD06 Disputed authorised transaction
Note: MD01 may be used for both a Return and a Refund.  To determine whether the transaction is a return or a refund:
fIf it is a return, the Originator value in the Return Reason Information field will be populated with a BIC.
fIf it is a refund, the Originator value in the Return Reason Information field will be populated with a Debtor Name.
May 2014
Pre-Settlement Rejects
The following table lists the reason codes that could occur for rejections or refusals or rejections from Bank of Ireland:
ISO Code SEPA Reason as specified in the Rulebook
AC01 Account identifier incorrect (i.e. invalid IBAN)
AC04 Account closed
AC06 Account blocked
Account blocked for direct debit by the Debtor
AG01 Direct debit forbidden on this account for regulatory reasons
AG02 Operation/transaction code incorrect, invalid file format
Usage Rule: To be used to indicate an incorrect ‘operation/transaction’ code
AM04 Insufficient funds
AM05 Duplicate collection
BE01 Debtor’s name does not match with the account holder's name
BE05 Identifier of the Creditor Incorrect
FF01 Operation/transaction code incorrect, invalid file format
Usage Rule: To be used to indicate an invalid file format.
FF05 Direct Debit type incorrect
MD01 No valid Mandate
MD02 Mandate data missing or incorrect
MD07 Debtor deceased
MS02 Refusal by the Debtor
MS03 Reason not specified
RC01 Bank identifier incorrect (i.e. invalid BIC)
RR01 Missing Debtor Account Or Identification
RR02 Missing Debtors Name Or Address
RR03 Missing Creditors Name Or Address
RR04 Regulatory Reason
SL01 Specific Service offered by the Debtor Bank
DNOR Debtor bank is not registered under this BIC in the CSM

