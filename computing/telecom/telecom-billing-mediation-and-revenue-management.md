---
id: computing/telecom/telecom-billing-mediation-and-revenue-management
canonical_question: How do telecom billing systems generate Call Detail Records (CDRs),
  perform mediation, rating, and interconnect settlement?
aliases:
- telecom billing tutorial
- CDR call detail record mediation
- telecom rating engine real time billing
- interconnect billing and roaming settlement
- prepaid vs postpaid billing architecture
entity_type: architecture_tutorial
domain: computing > telecom
last_verified: '2026-09-15'
---

# Telecom Billing and Revenue Management: CDR Generation, Mediation, Rating & Invoicing

## 1. Overview, Core Concepts & Scope

Telecom Billing
Telecom Billing
i
About the T utorial
Telecom Billing is a process of collecting usage, aggregating it, applying required charges,
and finally generating invoices for the customers. Telecom Billing process also includes
receiving and recording payments from the customers.
This tutorial gives you a complete understanding on Telecom Billing.
Audience
This tutorial has been designed for Telecom Billing Professionals . It  will help them
understand end-to-end billing process along with all the associated concepts.
Prerequisites
Before proceeding with this tutorial, we assume that you have a basic understanding of
GSM, GPRS services like voice, SMS and data.
Copyright & Disclaimer
© Copyright 2015 by Tutorials Point (I) Pvt. Ltd.
All the content and graphics published in this e-book are the property of Tutorials Point (I)
Pvt. Ltd. The user of this e-book is prohibited to reuse, retain, copy, distribute, or republish
any contents or a part of the contents of this e-book in any manner without written consent
of the publisher.
We strive to update the contents of our website and tutorials as timely and as precisely as
possible, however, the contents may contain inaccuracies or errors. Tutorials Point (I) Pvt.
Ltd. provides no guarantee regarding the accuracy, timeliness, or completeness of our
website or its contents including this tutorial. If you discover any errors on our website or
in this tutorial, please notify us at contact@tutorialspoint.com
Telecom Billing
ii
T able of Contents
About the Tutorial .................................................................................................................................. i
Audience ................................................................................................................................................ i
Prerequisites .......................................................................................................................................... i
Copyright & Disclaimer ........................................................................................................................... i
Table of Contents .................................................................................................................................. ii
1. TELECOM BILLING – INTRODUCTION ................................ ................................ ................. 1
Billing Systems ....................................................................................................................................... 2
Billing Types .......................................................................................................................................... 3
Billing System Vendors .......................................................................................................................... 3
2. TELECOM BILLING – SYSTEM ARCHITECTURE ................................ ................................ ..... 5
Typical Billing Process ............................................................................................................................ 6
Billing System Requirements .............................................

---

## 2. Technical Architecture, Workflows & Operational Methodologies

will discuss it in detail in the subsequent chapter "Invoice
Generation."
What is Next?
Next chapter would explain discount process, which is actually a part of rating and billing
process, but we kept it as a separate section because of the various that items need more
explanation.
We will discuss different types of discount hierarchies and which can be given at the time
of rating and billing.
Telecom Billing
33
All discounts alter (most commonly to reduce) the price to be paid for a set of events
and/or products. Discount is a way of giving customer money off. Discount defines a set
amount of money (percentage or monetary) to be applied to products or usage that meet
certain criteria. For example, all the local calls made on a particular day say 01 -01-2010
are charged at $0.20.
Discounts can be calculated either during the rating process or during the billing process:
 Rating Time Discount: All the discounts given at the time of rating process. These
discounts can be given at usage only. An example of rating time discount is "5%
off the first hour of all international calls".
 Billing Time Discount: All the discounts given at the time of billing process. These
discounts can be given on rated usage as well as on product & service charges. An
example of billing time discount is "5% off if you spend over $15 within a month".
A pre-itemization discount is one that modifies the price of each event to which it applies
to determine a rerated price. This discount also comes in billing time discount category ,
but this is related to rating of the calls. Other billing time discounts leave the price of the
event unmodified . A pre -itemization discount cannot incorporate product charges, only
event charges.
Discount Steps and Thresholds
The size of a discount is determined using a series of discount steps and thresholds.
Discount steps allow the size of the discount to be changed when particular thresholds are
reached.
For example, a discount for telephony events could depend upon the number of minutes
spent calling with 10 percent off after 100 minutes and 20 percent off after 200 minutes.
Each discount should have at least one step. Further steps can be added if the discount is
required to become more or less favorable with greater volumes. Each discount step can
have its discount expressed as either an amount of money or a percentage (but not both).
Simple Discount T ypes
There could be infinite types of discounts given to the end customer, but it depends on
what your billing supports. Following are the simple, but very good types of discounts ,
which can be offered:
Cross Product Discounts
These are the discounts where a set of products & events determine the discounts for
another set of products & events.
9. TELECOM BILLING - DISCOUNT APPLICATION
Telecom Billing
34
For example, "10 SMS free if more than $30 is spent on mobile calls". Here mobile calls
determine the discount and SMS product gets the discou nts, such type of discounts are
called cross product discounts.
Tiered Discounts
These are only applicable to the portion of the set of events or money spent that falls
between the assigned discount thresholds. For example, in the following di agram, 0% off
for a spend of $0-$100 threshold or 0-100 events threshold, 5% off for a spend of $100 -
$200 threshold or 100-200 events threshold, etc.
V olume Discounts
These are the discounts based on the number of events or product charges that a certain
product generates. For example, in the following diagram, 5% off for a  spend of $100 or
100 events, etc. As seen, the greater the spend, the more the discount.
Telecom Billing
35
T ax Discounts
Tax discounts provide an alternative method for dealing with  some tax exemptions. They
are calculated and applied when the account is billed.
Discount Periods & Proration
Most discounts have a discount period associated with them, which can be any number of
days, weeks, or months. This period can be used in three ways:
 To specify the time over which a threshold value is meant to be reached.
 To specify the frequency with which an absolute discount is meant to be applied.
 To specify how often the highest usage is determined for discounts with highest
usage filters attached.
Discounts could be pro -rated and non-prorated based on the requirement. If discount is
pro-rated, then discount will be calculated based on the number of days service has been
under use, and in case of non-proration discount, it will be calculated for the wh

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

activation, suspend, terminate,
quarantine, and again available.
Network Switches
Generally, Billing System does not interact with network switches. Network switches are
responsible to provide all the services to the end customers based on what services h ave
been provisioned for the customer. These systems are responsible for controlling calls,
data download, SMS transfer, etc., and finally, generating Call Detail Records.
Network Switches include MSC, SMSC, GGSN , and MMSC. For more information on GSM,
MSC, SMS, SMSC, GGSN, MMS, MMSC, please refer to our GSM tutorials.
Telecom Billing
74
Mediation System
The Mediation System collects CDRs from different network elements in different formats.
Various network elements generate CDRs in ASN.1 format and some network elements
have their own proprietary format of CDRs.
The Mediation System processes all the CDRs and converts them into a format compatible
to the downstream system, which is usually a Billing System. The Mediation System applies
various rules on CDRs to process them; for example, mediation system marks the
international calls based on the dialed number (B -Number), same way mediation system
marks the on-net calls based on A-Number and B-Number.
There may be a requirement to filter out all the calls, which are having call duration less
than 5 seconds, the best place to filter out such type of calls will be at Mediation System
level. Same way, if some extra information is required in the CDRs , which is critical to
billing, then Mediation System will help in providing such information based on some other
attributes available within the CDRs.
Once the collected CDRs are processed, Mediation System pushes all the CDRs to the
Billing System using FTP because usually Med iation and Billing systems run on different
machines.
Data Ware House (DWH) System
This is a downstream system for the Billing System and usually keeps tons of historical
data related to the customers. Billing System dumps various customer information into
the DWH system. This information includes service usage, invoices, payments, discounts
and adjustments, etc.
All this information is used to generate various types of management reports and for
business intelligence and forecast.
DWH system is always mean t to work on bulk and huge data, and if there is a need for
any small report, then it is always worth to generate it from the billing system directly
instead of abusing DWH for a small task.
Enterprise Resource Planning (ERP)
An Enterprise Resource Plannin g (ERP) system provides modules to handle Financials,
Human Resources and Supply Chain Management, etc.
Billing System interface with this system is used to post all the financial transactions like
invoices, payments, and adjustments.
This system works lik e a general ledger for the finance department and gives complete
revenue information at any point in time it is required.
Payment Gateway
As such, this is not necessarily a complete system, but it could be a kind of custom
component, which sits in between the Billing System and different payment channels like
banks, credit card gateway, shops, and retailers, etc.
Telecom Billing
75
All the payment channels use payment gateway to post payments to the billing system to
settle down customer invoices.
Usually, Payment gateway exp oses a kind of API (Application Programming Interface) to
the outside world to post the payments to the Billing System. The API can be used by any
external resource to post the payment.

