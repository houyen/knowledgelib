---
id: finance/payments/sepa/sepa-credit-transfer-banking-operations
canonical_question: How do core banking payment engines process inbound and outbound
  SEPA Credit Transfers?
aliases:
- SEPA credit transfer banking engine
- outbound SCT processing
- inbound SCT clearing
- EBA STEP2 integration
- SCT dispatch and recall processing
entity_type: core_banking_guide
domain: finance > payments > sepa
last_verified: '2026-09-15'
---

# SEPA Credit Transfer Operations and Clearing Integration (Oracle Banking Payments)

## 1. Overview & Executive Summary

SEPA Credit Transfer User Guide
Oracle Banking Payments
Release 14.5.0.0.0
Part No. F42401-01
May 2021
1-1
SEPA Credit Transfer User Guide
Oracle Financial Services Software Limited
Oracle Park
Off Western Express Highway
Goregaon (East)
Mumbai, Maharashtra 400 063
India
Worldwide Inquiries:
Phone: +91 22 6718 3000
Fax: +91 22 6718 3001
www.oracle.com/financialservices/
Copyright © 2017, 2021, Oracle and/or its affiliates. All rights reserved.
Oracle and Java are registered trademarks of Oracle and/or its affiliates. Other names may be trademarks of their respective
owners.
U.S. GOVERNMENT END USERS: Oracle programs, including any operating system, integrated software, any programs
installed on the hardware, and/or documentation, delivered to U.S. Government end users are “commercial computer software”
pursuant to the applicable Federal Acquisition Regulation and agency-specific supplemental regulations. As such, use,
duplication, disclosure, modification, and adaptation of the programs, including any operating system, integrated software, any
programs installed on the hardware, and/or documentation, shall be subject to license terms and license restrictions applicable
to the programs. No other rights are granted to the U.S. Government.
This software or hardware is developed for general use in a variety of information management applications. It is not developed
or intended for use in any inherently dangerous applications, including applications that may create a risk of personal injury. If
you use this software or hardware in dangerous applications, then you shall be responsible to take all appropriate failsafe,
backup, redundancy, and other measures to ensure its safe use. Oracle Corporation and its affiliates disclaim any liability for
any damages caused by use of this software or hardware in dangerous applications.
This software and related documentation are provided under a license agreement containing restrictions on use and disclosure
and are protected by intellectual property laws. Except as expressly permitted in your license agreement or allowed by law, you
may not use, copy, reproduce, translate, broadcast, modify, license, transmit, distribute, exhibit, perform, publish or display any
part, in any form, or by any means. Reverse engineering, disassembly, or decompilation of this software, unless required by
law for interoperability, is prohibited.
The information contained herein is subject to change without notice and is not warranted to be err

---

## 2. Core Operational & Technical Architecture

he Application toolbar.
You can click ‘Search’ button to view all the pending functions. However, you can to filter your
search based on any of the following criteria:
 Transaction Reference Number
 Sender Transaction ID
 Sender End to End ID
 File Reference Number
 Network Code
 Source Code
 Authorization Status
 Booking Date
 Instruction Date
 Activation Date
 Transfer Currency
 Transfer Amount
 Maker ID
 Checker ID
 Transaction Branch
 Creditor Account IBAN
 Customer Number
 Customer Service Model
2-48
 Debtor Account IBAN
 Debtor Bank Code
When you click ‘Search’ button the records matching the specified search criteria are
displayed.
Double click a record or click ‘Details ‘button to view the detailed maintenance screen.
2.4.2 Inbound  ACH Payments Transaction View
User can view the complete details about the ACH Inbound transaction, approvals from the
system, Queue actions, and all the details pertaining to the transaction in this screen.
You can invoke “Inbound Low Value Payments (ACH) View” screen by typing ‘PADIVIEW’ in
the field at the top right corner of the Application tool bar and clicking on the adjoining arrow
button. Click new button on the Application toolbar.
 From this screen, click Enter Query. The Transaction Reference field gets enabled
which opens an LOV screen.
 Click the Fetch button and select the required value.
 Along with the transaction details in the Main and Pricing tabs user can also view the
Status details for the following:
– External System Status
– Transaction Status
– Pending Queue Details
– Sanction Seizure
 Click Execute Query to populate the details of the transaction in the ACH Inbound
Payments View screen.
For more details on Main and Pricing tabs refer to ‘PADITONL’ screen details above.
2-49
2.4.2.1 Exceptions Tab
Click the Exceptions Tab to invoke this screen and specify all the required details.
2.4.2.2 View Queue Action Log
You can invoke this screen by clicking ‘View Queue Action’ tab in the PADIVIEW screen. For
more details on the fields refer to section 2.2.2.2
.
2-50
2.4.2.3 UDF Tab
You can invoke this screen by clicking UDF tab in the PADIVIEW screen.
2.4.2.4 MIS Tab
You can invoke this screen by clicking MIS tab in the PADIVIEW screen.
2.4.2.5 View Repair Log
You can invoke this screen by clicking ‘View Repair Log’ tab in the PADIVIEW screen. For
more details on the fields refer to section 2.2.2.5
2-51
.
2.4.2.6  Accounting Entries Tab
You can invoke this screen by clicking Accounting Entries tab in the PADIVIEW screen. For
more details on the fields refer to section 2.4.1.6
.
2-52
2.4.2.7 ACH Inbound Payments View Summary
You can invoke the ‘Inbound Low Value Payments (ACH) View Summary’ screen by typing
‘PASIVIEW’ in the field at the top right corner of the application toolbar and clicking the
adjoining arrow button.Click new button on the Application toolbar.
You can search for the records using one or more of the following parameters:
 Transaction Reference Number
 Sender Transaction ID
 Sender End to End ID
 File Reference Number
 Network Code
 Source Code
 Source Reference Number
 FX Reference Number
 Credit Liquidation Status
 Booking Date
 Instruction Date
 Activation Date
 Transfer Currency
 Transfer Amount
 Sanctions Check Status
 External Account Check Status
2-53
 Transaction Branch
 Creditor Account IBAN
 Customer Number
 Customer Service Model
 Debtor Account IBAN
 Debtor Bank Code
 Linked Transaction Reference
 Exception Queue
Once you have specified the search parameters, click ‘Search’ button. The system displays
the records that match the following search criteria.
Double click a record or click ‘Details’ button to view the detailed maintenance screen.
2.5 ACH Inbound Transaction Processes and Validations
2.5.1  Inbound File Upload
Background job are available for reading the Inbound SCF file from the designated folder and
to populate the data into staging table

---

## 3. Specifications, Standards & Lifecycle Operations

ased bulk messages to be generated or ISO
messages. This is an optional maintenance. If this maintenance is not available, the system
generates EBA specific SEPA files. This is applicable to ACH CT and Direct Debits.
You can invoke ‘SEPA Messaging Preferences’ screen by typing ‘PMDSEPAM’ in the field at
the top right corner of the Application tool bar and clicking on the adjoining arrow button. Click
’New’ button on the Application toolbar.
You can specify the following fields:
Host Code
The system defaults the host code of transaction branch on clicking ‘New’
Network Code
Specify the Network Code from the list of values.
Network Type
The system defaults the Network Type on selecting the Network Code.
2-103
Network Description
The system defaults the Network Description on selecting the Network Code.
File Format Details
Non-CSM based files
Select the value between Yes or No.
If the filed value is 'Yes' then SEPA ISO messages are generated for each transaction type.
If SEPA Message preferences is available and the Non -CSM based files is set as 'Yes', then
dispatch file generation is based on the EPC ISO message formats.
 Separate files are generated for the message type
 Files are generated for transactions with current date as instruction date. If back dated
transactions are there settlement date is moved to current date
 Files are generated for the dispatch cycles maintained in Dispatch Parameters for the
Network and service type SCT
 Number of transactions restrictions for batch is considered for total number of
transactions allowed in a message
 File size restriction, if maintained in dispatch parameter is applicable
2.9.1.1 SEPA Messaging Preferences Summary
You can invoke the ‘SEPA Messaging Preferences Summary’ screen by typing ‘PMSSEPAM’
in the field at the top right corner of the application toolbar and clicking the adjoining arrow
button.Click new button on the Application toolbar.
You can click ‘Search’ button to view all the pending functions. However, you can to filter your
search based on any of the following criteria:
 Authorization Status
 Network Code
 Non-CSM based files
 Record Status
 Network Type
2-104
When you click ‘Search’ button the records matching the specified search criteria are
displayed. Double click a record or click ‘Details ‘button to view the detailed maintenance
screen.
3-1
3. Function ID Glossary
P
PADINRCL ......................2-66
PADINRTN ......................2-86
PADIRCLV ......................2-70
PADIRTVW .....................2-90
PADITONL ......................2-34
PADITRCL ......................2-77
PADIVIEW .......................2-48
PADORCLV .....................2-63
PADORTVW ....................2-84
PADOTONL .......................2-1
PADOTRCL .....................2-58
PADOTRTN .....................2-81
PADOVIEW .....................2-19
PADRCRES ....................2-73
PASINRCL ......................2-69
PASINRTN ...................... 2-89
PASIRCLV ...................... 2-71
PASIRTVW ..................... 2-91
PASITONL ...................... 2-47
PASITRCL ...................... 2-80
PASIVIEW ...................... 2-52
PASORCLV .................... 2-65
PASORTVW .................... 2-85
PASOTONL .................... 2-17
PASOTRCL ..................... 2-61
PASOTRTN .................... 2-83
PASOVIEW ..................... 2-24
PASRCRES .................... 2-75
PMDNCPRF ...................... 2-7
PMDSEPAM .................. 2-102
PMSSEPAM .................. 2-103

