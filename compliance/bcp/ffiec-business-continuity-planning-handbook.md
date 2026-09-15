---
id: compliance/bcp/ffiec-business-continuity-planning-handbook
canonical_question: What are the regulatory examination standards for Business Impact
  Analysis (BIA), Disaster Recovery (DR), and continuity testing?
aliases:
- FFIEC BCP handbook
- business impact analysis BIA methodology
- recovery time objective RTO RPO
- disaster recovery testing scenarios
- financial institution continuity planning
entity_type: regulatory_handbook
domain: compliance > bcp
last_verified: '2026-09-15'
---

# FFIEC Business Continuity Planning (BCP) Examination Handbook

## 1. Overview, Core Concepts & Scope

MARCH 2003
Federal Financial Institutions Examination Council
FFIEC
IT EXAMINATION
HANDBOOK
BCP
Business
Continuity Planning
TABLE OF CONTENTS
INTRODUCTION................................................................................ 1
BOARD AND SENIOR MANAGEMENT RESPONSIBILITIES ......... 3
BUSINESS CONTINUITY PLANNING PROCESS............................ 4
Business Impact Analysis .....................................................................................6
Risk Assessment ..................................................................................................8
Risk Management...............................................................................................10
Business Continuity Plan Development ...................................................10
Other Policies, Standards and Processes...........................................................12
Systems Development Life Cycle and Project Management....................12
Change Control........................................................................................13
Data Synchronization ...............................................................................13
Employee Training and Communication Planning....................................13
Insurance .................................................................................................14
Government and Community ...................................................................15
Risk Monitoring ...................................................................................................15
Overall Testing Strategy...........................................................................15
Testing Scope and Objectives..................................................................16
Specific Test Plans...................................................................................17
Test Plan Review .....................................................................................17
Validation of Assumptions........................................................................17
Accuracy of Information............................................................................18
Completeness of Procedures...................................................................18
Testing Methods.......................................................................................18
ORIENTATION/WALK-THROUGH ......................................................... 18
TABLETOP/MINI-DRILL.......................................................................... 18
FUNCTIONAL TESTING ......................................................................... 19
FULL-SCALE TESTING .......................................................................... 19
Conducting a Test ....................................................................................20
Analyzing and Reporting Test Results .....................................................20
Updating a Business Continuity Plan .......................................................21
Audit and Independent Reviews...............................................................21
SUMMARY.................................

---

## 2. Technical Architecture, Workflows & Operational Methodologies

nvolv ement in the business continuity program is effective,
including:
• Audit coverage of the business continuity program;
• Assessment of business continuity preparedness during line(s) of business
reviews;
• Audit participation in testing in an observer role; and
• Audit review of testing plans and results.
Objective 6: Determine whether the BCP( s) include(s) appropriate testing to
ensure the business proc ess(es) will be maintained, resumed, and/or
recovered as intended.
1. Determine if the BCP(s) is tested at least annually.
2. Verify that all critical business units/departments/func tions are included in the
testing.
3. Verify that tests include:
• Setting goals and objectives in advance;
• Realistic conditions and activity volumes;
• Use of actual back-up system and data files while maintaining off-site back-up
copies for use in case of an event concurrent with the testing;
• Participation and review by internal audit;
• A post-test analysis report and review process that includes a comparison of test
results to the original goals;
• Development of a corrective action plan(s) for all problems encountered; and
• Board of directors review.
4. Determine if interdependent departme nts, vendors, and key market providers
have been involved in testing at the same time to uncover potential conflicts
and/or inconsistencies.
5. Determine if the level of testing is adequate for the size and complexity of the
organization.  Determine if  the testing includes:
Business Continuity Planning Booklet - March 2003
FFIEC IT Examination Handbook  Page A-8
• Testing the operating systems and utilities (infrastructure);
• Testing of all critical applications (application level);
• Data transfer between applications (integrated testing); and
• Testing the complete environment and workload (stress test).
6. Determine whether testing at an alternative location includes:
• Network connectivity;
• Items processing and backroom operations connectivity and information; and
• Other critical data feed connections/interfaces.
7. Determine whether testing of the inform ation technology infrastructure includes:
• Rotation of personnel involved; and
• Business unit personnel involvement.
8. Determine whether management considered testing with:
• Critical service providers;
• Customers;
• Affiliates;
• Correspondent institutions; and
• Payment systems and major financial market participants.
Objective 7: Determine if the inform ation technology environment has a
properly documented BCP that comple ments the enterprise-wide and other
departmental BCPs.
1. Verify that the IT BC P properly supports and reflects the goals and priorities
found in the business unit BCP(s).
2. Determine if all critical resources and technologies are covered by the BCP(s),
including voice and data communication networks, customer delivery channels,
etc.
Business Continuity Planning Booklet - March 2003
FFIEC IT Examination Handbook  Page A-9
3. Determine if the BCPs  include the entire ne twork and communication
connections.
4. Determine if the BCP es tablishes processing priorities to be followed in the
event not all applications can be processed.
Objective 8: Determine whether the BC P(s) include(s) appropriate hardware
backup and recovery.
1. Describe the arrangement s for alternative processing capability in the event any
specific hardware, the data center, or any portion of the network becomes
disabled or inaccessible, and determin e if those arrangements are in writing.
2. If the organization is relying on in-house systems at separate physical locations
for recovery, verify if the equipment is  capable of independently processing all
critical applications.
3. If the organization is re lying on outside facilities for recovery, determine if the
recovery site:
• Has the ability to process the required volume;
• Provides sufficient processing time for the anticipated workload based on
emergency priorities; and
• Allows the organization to use the facility until it achieves a full recovery from
the disaster and resumes activity at the organization’s own facilities.
4. Review the contract between applicable  parties, such as recovery vendors.
5. Determine how the recovery facility’s  customers would be accommodated if
simultaneous disaster conditions were to occur to several customers during the
same period of time.
6. Determine whether the organization ensures that when any changes (e.g.
hardware or software upgr ades or modifications) in  the production environment

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

data integrity, client confidentiality, and the physical security of
hardcopy output, media, and hardware.
OFF-SITE STORAGE
The off-site storage location should be e nvironmentally controlle d and secure, with
procedures for restricting physical access to au thorized personnel.  Moreover, the off-site
premises should be an adequate distance from the computer operations location so that
both locations will not be impacted by the same event.  Beyond a copy of the BCP,
duplicate copies of all necessary procedures , including end of day, end of month, end of
quarter, and procedures covering relatively rare and unique issu es should be stored at the
offsite locations.  Another alternative to consider would be to  place the critical
information on a secure shared network drive,  with the data back ed up during regularly
scheduled network back-up.  However, this shared drive should be in a different physical
location that would not be affected by th e same disruption.  Management needs to
maintain a certain level of non-networked (e.g., hardcopy) mate rial in the ev ent that the
network environment is not available for a period of time.
Reserve supplies, such as forms, manuals, lett erhead, etc., should also be maintained in
appropriate quantities at an off-site locati on and management should maintain a current
inventory of what is held in the reserve supply.
FACILITIES
The BCP should address site relocation for sh ort-, medium- and long-term disaster and
disruption scenarios.  Continuity planning for recovery facilities should consider location,
size, capacity (computer and telecommunicatio ns), and required amenities necessary to
recover the level of service required by the critical busine ss functions.  This includes
planning for workspace, telephones, worksta tions, network connectivity, etc.  When
determining an alternate processing site, mana gement should consider scalability, in the
event a long-term disaster becomes a realit y.  Additionally, during the recovery period,
the BCP should be reassessed to determine if te rtiary plans are warranted.  Procedures to
utilize at the recovery location should be developed.  In addition, any files, input work, or
specific forms, etc., needed at the back-up site should be specified in the written plan.
The plan should include logistical procedur es for moving personnel to the recovery
location, in addition to steps to obtain the materials (media, documentation, supplies, etc.)
Business Continuity Planning Booklet - March 2003
FFIEC IT Examination Handbook  Page E-8
from the off-site storage location.  Plans for lodging, meals, and family considerations
may be necessary.
COMMUNICATION
Communication is a critical aspect of a BCP and should include communication with
emergency personnel, employees, directors,  regulators, vendors/ suppliers (detailed
contact information), customers (notificati on procedures), and the media (designated
media spokesperson).  Alternat e communication channels shoul d be considered such as
cellular telephones, pagers, sate llite telephones, and Internet  based communications such
as e-mail or instant messaging.
OTHER CONSIDERATIONS
Each financial institution is different and processes will vary.  However, management
should consider how to accomplish the following:
• Prevention and preparedness;
• Reconciling recovery times with business unit requirements;
• Disaster declaration and plan implementation processes;
• Recovery progress reporting; and
• Testing of the plans.

