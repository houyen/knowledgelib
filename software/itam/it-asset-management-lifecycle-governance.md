---
id: software/itam/it-asset-management-lifecycle-governance
canonical_question: How do enterprises establish governance policies, risk controls,
  and cost optimization for IT assets?
aliases:
- IT asset management governance
- managing IT assets guide
- ITAM policy framework
- shadow IT asset discovery
- total cost of ownership IT assets
entity_type: governance_guide
domain: software > itam
last_verified: '2026-09-15'
---

# IT Asset Management Governance: Policies, Risk Mitigation, and Cost Optimization

## 1. Overview, Core Concepts & Scope

Managing IT Assets
Phillip J. Windley, Ph.D.
Chief Information Officer
Office of the Governor
State of Utah
Organizations usually have an inventory control function that is designed to track
large capital assets.  When organizations track IT assets, however, the
techniques used to track other capital assets may fall short and not deliver all the
possible value to the organization.  In addition, many benefits over and above
financial tracking are lost.  This paper discusses IT capital asset management
and describes the benefits that accrue from doing it properly.
Throughout this paper, we will talk of an asset management system.  This
system could be an integrated piece of software that performs all of the functions
discussed below.  However, it may be something much simpler than that or even
various components held together through process.  The decision of what kind of
system is necessary depends on the size of the asset pool and the needs of the
organization managing the assets.
Asset Lifecycle
Before we talk about tracking and managing IT assets, we should discuss the
asset lifecycle since the asset management will take place within the context of
this lifecycle.  Figure 1 shows the asset lifecycle that will be used throughout this
paper.
Procurement Deploy Use
Upgrade
Decommission
Salvage
Figure 1: Asset Lifecycle
 Copyright 2002, Phillip J. Windley.  All rights reserved.  Reproduction of all or part of this work is
permitted for educational or research use provided that this copyright notice is included in any copy.
Unconditional use is granted to the State of Utah.
The first phase in the asset lifecycle is procurement.  When an asset is procured
it enters the asset management system and begins to be managed.  Ideally, the
procurement system should feed the asset management system the data on the
new asset as soon as the purchase order is completed and the receiving
organization should acknowledge receipt in a way that confirms the asset in the
asset management system and notifies the purchasing system so that payment
can be made.
The second phase of the asset lifecycle is deployment.  When an asset is
deployed, the system should be updated with relevant data such as location,
responsible party in the organization, configuration, vendor, warranty, and any
other data that will be useful in managing the asset.  The location may be a
physical location or simply a link to some other asset that contains the asset
being deployed.  For example, software or memory will likely be tied to a chassis
and be located wherever that chassis is located.
The third phase of the asset management cycle is usage.  Usage is not simply a
static flag but could be periodically updated by operational software that
measures asset usage so that valuable assets not being used can be
redeployed.
From time to time, the asset in question might be upgraded in some way.  The
software version may be changed, or a new hard drive may be added.  When this
happens the configuration information for the asset should be updated
accordingly.
When an asset is no longer being used, it is decommissioned.
Decommissioned assets may still be useful to the organization, in which case
th

---

## 2. Technical Architecture, Workflows & Operational Methodologies

arranty information for assets to avoid paying for repairs to equipment that
should be covered by the vendor or manufacturer.
Software License Compliance.  Clearly one of the major tasks facing the
financial division of any large IT organization is tracking software licenses and
ensuring that they are properly allocated and used.  Being out of compliance can
bring financial risk, but more often becomes a time sink as the IT organization
focuses on coming into compliance instead of adding value to the mission of the
organization they serve.
Operational Monitoring and Control.  IT assets must be operated to add value
to the organization.  In most cases, this operation is split between an
administrator who maintains the asset in a functioning state and the employee or
employees who use the asset to produce value.  The administration of the IT
asset can be a large task.  Often, IT organizations take advantage of the
economies of scale that computers allow and administer them using operational
monitoring and control systems.  The asset management system can form the
basis for the operational system and supply vital information needed by the
operational system when an asset is deployed or remove it when the asset is
decommissioned.
Decision Making About IT Resource Deployment.  Often IT assets are
deployed with little understanding of how they will be used and in many cases
they are not used as they were originally intended.   For example, a computer
may be deployed and then rarely used or it might be deployed and overused.
When data from the asset management system is combined with operational
data, these patterns can be easily seen and resources reallocated to better add
value to the organization.
Zero-day Employee Provisioning.   Employees are expensive.  Keeping them
functioning is a critical issue.  This is true from the very start.  A good asset
management system can form the basis for and facilitate zero-day employee
provisioning.  In zero-day employee provisioning, an employee should show up
4
for work (whether just starting in the organization or simply changing positions)
with everything the employee needs to start work and be productive.  Clearly, in
today’s world this includes a computer that is properly set-up and configured with
the right software to get the job done, access to appropriate data, a phone, and
other devices.  On the other end of the employee lifecycle, when an employee
leaves the organization, their access to data and systems should be rescinded
and any equipment they were responsible for should move to the
decommissioning phase so that its available for redeployment.
Standardization and Compliance.  Non-standard equipment and software cost
an organization money.  Non-standard IT infrastructure requires more employees
to manage and those employees are less productive because they are less likely
to be experts at managing the non-standard asset.  In addition, time is wasted
when people are required to use and understand non-conforming data and
systems.  An asset management system can tell an organization the level of
compliance with standards and allow efforts to bring the IT infrastructure into
compliance to be focused on the areas where they are most needed.
More Informed Purchasing.   When combined with operational data, the asset
management system can help an organization evaluate past purchasing
decisions and make better decisions in the future.   An asset management
system can track vendors and provide data about how one vendor performs
relative to another in key areas such as delivery, support, etc.
Business Resumption Support.  Whether assets are lost through disaster or
something less severe (such as theft or damage), a properly functioning asset
management system can help the business resume its operations more quickly.
From knowing what assets are being used to how they are configured, an asset
management system contains data that is vital to a recovery from disaster.
Performance Metrics
The following performance metrics should be tracked in relation to the asset
management system to determine its effectiveness:
Total Cost of Ownership (TCO).  Total cost of ownership, while based on
operational measures to some extent is, in the end, a financial measure.  One of
the reasons for having an asset management system is to reduce costs.  While
asset management does not account for all of the factors in TCO, it is clearly the
foundational process for managing TCO and, ultimately, reducing it

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

organization evaluate past purchasing
decisions and make better decisions in the future.   An asset management
system can track vendors and provide data about how one vendor performs
relative to another in key areas such as delivery, support, etc.
Business Resumption Support.  Whether assets are lost through disaster or
something less severe (such as theft or damage), a properly functioning asset
management system can help the business resume its operations more quickly.
From knowing what assets are being used to how they are configured, an asset
management system contains data that is vital to a recovery from disaster.
Performance Metrics
The following performance metrics should be tracked in relation to the asset
management system to determine its effectiveness:
Total Cost of Ownership (TCO).  Total cost of ownership, while based on
operational measures to some extent is, in the end, a financial measure.  One of
the reasons for having an asset management system is to reduce costs.  While
asset management does not account for all of the factors in TCO, it is clearly the
foundational process for managing TCO and, ultimately, reducing it.
Illegal Software Usage and Risk of Non-Compliance.  In an IT asset
management system, one key reason for managing the software licenses, is to
reduce illegal software usage and, as a result, the risk to the organization of non-
compliance with the terms of the license.  Non-compliance and the resultant risk
should be regularly tracked and reported.
5
6
Accuracy of System.  The accuracy of the system will depend, in large
measure, on how much money and time the organization is willing to spend on
the original system and its operation.  We could, of course, strive for 100%
accuracy, but this is not realistic from a time or cost standpoint.  The accuracy of
the system must be balanced against the return on investment for increased
accuracy.  For small organizations with a small capital investment and where the
risk of software non-compliance is relatively low, the system might only need to
be 95% accurate to fulfill its mission (although such low accuracy might decrease
its usefulness as a basis for the operational systems).  For large organizations, a
more accurate system may be required to meet the needs of the organization.
For each of these performance measures, some form of audit will be required to
establish the organization’s performance against the measurements.
Conclusion
While knowing what IT assets are in use and how they are configured may seem
like mundane issues, it is vital to both the financial health of the IT organization
and its operational performance.
Not knowing what we have is costly.  In fact, I’ve had vendors tell on more than
one occasion that they make their money by knowing what assets we own better
than we do and selling us more than we really need (they usually confess this
after they are no longer selling to me).
An asset management system is an important, foundational piece of the overall
systems necessary to manage IT infrastructure.  Without a good asset
management system the organization will waste time and resources managing
inventory, buying unnecessary equipment and software, and maintaining license
compliance for software.  With a functioning asset management system the
organization can expect to reduce the total cost of ownership for IT infrastructure
and provide a solid foundation for the operational system necessary to keep the
infrastructure operating efficiently.

