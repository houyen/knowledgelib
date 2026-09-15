---
id: software/crm/salesforce/salesforce-flow-and-formulas-cheatsheet
canonical_question: What are the essential formulas, flow logic patterns, and validation
  rules in Salesforce administration?
aliases:
- Salesforce cheatsheet
- Salesforce formula functions
- Salesforce validation rule syntax
- Flow Builder design patterns
- Salesforce admin reference
entity_type: technical_cheatsheet
domain: software > crm > salesforce
last_verified: '2026-09-15'
---

# Salesforce Ultimate Cheatsheet: Formulas, Flow Builder, and Validation Rules

## 1. Overview, Core Concepts & Scope

S A LES FO R C E
U LTIM A TE
C H EA TS H EET
Phone/Whatsapp: +1 (515) 309-7846 (USA)
Email: info@zarantech.com
Website: www.zarantech.com
CRM Cheatsheet
When you’reworking a lead, setup a series of tasksbased on the typeof lead.
Use email marketing and call downs to re-market to unqualified or no-contact leads
Create a set of Opportunity isqualification assigned manually questions, such as on conversion current situation, (lead owner). If product of interest, automatic timeframe, key assignment is decision makers.needed use custom package
If the lead is workflow rules.qualified, convert it to a contact, Monitor your with an associated opportunities opportunityreports and and account.dashboards to keep track of top deals andprioritize your time.
EmailmarketingDirect mailCold callsPartnersTV
Radio EventsTrade showsPR
Opportunity teams Opportunity splits Products & Pricebooks CPQApprovalDocument generation Digital signature Forecasting
Customize Salesforce to fit your internal sales processes, making iteasier to monitor your sales pipeline
Set up different views to manageyour leads.For example, today’s leads or leads sorted by lead type.
Set upduplicatemanagementto preventduplicates atthe point ofentry. Manuallymerge legacyrecords.
Salesforce gives your entire company a 360-degree view of yourcustomers and facilitatescollaboration across yourorganization, helping you build strong, lastingcustomer relationships.
LISTS
INBOUND CALLS
WEBSITE & SOCIAL
WORKING LEADS
ARCHIVE YOUR DEAD LEADS
QUAL I F I ED?
IMPORT DATA
CREATE NEW LEADS
WEB-TO-LEAD FORM
OPPORTUNITIES
LEAD CAPTURE MY OPEN LEADS
ARCHIVE YOUR DEAD OPPORTUNITIES
PRESENTATION, PROPOSAL, NEGOTIATION WON
DUPLICATE LEAD?
•••
•••
•••••
•••
• Referrals •Google Maps
Purchased listTrade showLegacy data
•Organic web traffic•Email responses •Social mentions
For example:
Day 1: Personalizemass emailDay 2: Call/voicemail
Day 3: Call/
voicemail
Day 4: Personalize
mass email
•Search first, then create a new lead in Salesforce
•Use the import wizard or data loader
Free trial“Contact me”request Eventregistration
•Set up auto-response emails:“Thank you for your interest”•Your trial information
•Event details
•Set up lead assignment rules– Geography–Company size–Product of interest
Use email marketing and calldowns to re-market to ClosedLost opportunities
PLAN AND EXECUTE MARKETING CAMPAIGN
•
Marketing
Support
Sales
1 1 1 1
Phone/Whatsapp: +1 (515) 309-7846 (USA) Email: info@zarantech.com
www.zarantech.com
Service Cloud Cheatsheet
•Incoming calls
•Website visits •Social mentions•Community posts
Incoming emailsIncoming chats Video calls & more
Automatically                Track Key escalate cases open       Performancebeyond a certain           Indicators (KPI)period of time or           and importantwhere an SLA               service metrics has expired.                 including average                                    resolution time,                                    first call                                    resolution,                                    and customer                                    satisfaction.
•Automatically createcases from emails & incoming chats
•Search in Salesforce and upd

---

## 2. Technical Architecture, Workflows & Operational Methodologies

all Contacts be associated with an
Account).
All Contacts are associated with a single Account, as if all of your contacts have been
dumped in one "bucket".
B2C account models
Account Hierarchy models
Contacts to multiple Accounts models
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
Data migration & Backup
Data governance & stewardship
Data Loading best practices:
•Use BULK API for more that a few thound records
•Use the fastest operation Insert > Update > Upsert
•Use Public Read/Write security to avoid sharing calculation
•Disable triggers, workflow rules and validation
•Some fields might be transformed during migration (id, autonumber, audit fields)
•When changing child records, group them by parent Id
•Use defer-sharing
•Activate sharing rules after loading and one at a time
•Audit fields can be populated only on insert.
Backup types:
• Full
• Incremental
• Partial
Data archiving options:
•BigObject
•Outside of Salesforce
•Weekly export
•Data loader
•Reporting snapshot
Data governance is a process to ensure usability, quality, and policy compliancce of the data asset. It includes
business definitions, data quality and security rules, supports UI and integration design.
It defines what is collected, how is it kept secured, who can CRUD, what quality rules are there, how available
and usable is the data, ...
Data stewardship is a cross-functional tactical role and activities to ensure adherence to data governance rules
and spirit. It includes data quality monitoring, work flow, and maintenance.
Mastar data management is the effort made by an organization to create one single master reference source
for all critical business data, leading to fewer errors and less redundancy in business processes. It consists of 3
pillars: Mastering data, Mastering data relationships and Mastering events.
Understand the linear flow of data:
How are records generated?
Why are they created?
What are they used for?
What is reported on?
Where is the hand-off?
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
Single Sign On Methods
Methods to provision users
Self-registration
Mass user provisioning
Identity connect with AD
Social sign-on provisioning
Method
Manual provisioning
API provisioning
Programmatic provisioning
JIT provisioning with SAML
Description
A user is created manually by an administrator.
Provision users by using the SOAP or REST API on theUser object.
Povision users in Apex code.
Use a SAML assertion to create regular and portal users on the fly the first
time they try to log in. This eliminates the need to create user accounts in advance.A user is created when he logs in via SSO.
Create a large number of users by using Bulk API, Data Loader or an ETL tool.
Integrates Microsoft Active Directory (AD) with Salesforce. User information
entered in AD is shared with Salesforce seamlessly and instantaneously. Companies that use AD for user management can use Identity Connect to manage Salesforce accounts.Changes in AD are reflected in Salesforce in near real time.
Users can self-register when first visiting the site. Works with community users only.
Users can sign in using a social site credentials. Supported sites include
LinkedId, Facebook, Twitter, Google, Janrain, Salesforce, and any srevice who implements the OpenID Connect protocol or Oauth. Works with community users only.
Method
SSO with multiple Orgs
SSO with AD
Social Sign On
Federated Authentication
Delegated Authentication
Description
SSO between multiple Salesforce orgs. Can be enabled in Setup for both
orgs. Works only with internal users.
Salesforce is integrated with AD using Identity Connect or ADFS
Sign on via a Social site credentials. Works with community users only.
The platform receives a SAML assertion in an HTTP POST request. The SAML
assertion has a limited validity period, contains a unique identifier, and is
digitally signed. If the assertion is still within its validity period, has an identifier
that has not been used before, and has a valid signature from a trusted identity
provider, the user is granted access to the application. If the assertion fails
validation for any reason, the user is informed that their credentials are invalid.
An internal WS authenticates users. It receives an username, password and
sourceIP and returns true or false.
*Never enable SSO for Admin users
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515)

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

ign-on.
Example: SSO with a company credentials(AD) using Salesforce App which then connects to
Salesforce
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
OAuth & SSO Flow diagrams
Canvas App User Flow - Signed Request
The default method of authentication for canvas apps. The signed request authorization flow varies
depending on whether you configure the canvas app so that the administrator gives users access to
the canvas app or if users can self-authorize. The signed request containing the consumer key,
access token, and other contextual information is provided to the canvas app if the administrator
has allowed access to the canvas app for the user or if the user has approved the canvas app via the
approve/deny OAuth flow.
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
OAuth & SSO Flow diagrams
Canvas App User Flow - Oauth
Canvas apps can use the OAuth 2.0 protocol to authenticate and acquire access tokens.
If your canvas app uses OAuth authentication, the user experience varies depending on where the
canvas app is located in the user interface and how the user access is set. This diagram shows the
user flow for a canvas app that uses OAuth authentication.
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
OAuth & SSO Flow diagrams
SP Initiated SAML SSO
SAML Single Sign-On for Canvas Apps
With this feature you can create a canvas app that begins a standard SAML authentication flow
when opened by a user. After this process completes, the user is authenticated into your Web
application.
For canvas apps that use signed request authentication, two methods that are included in the
Canvas SDK enable your canvas app to call into Salesforce to receive a new signed request directly
or enable Salesforce to repost the signed request to your Web application endpoint. This results in a
complete end-to-end authentication flow.
refreshSignedRequest Method
Returns a new signed request via a callback. After the SAML SSO process is completed, your app can
call this method and receive a new signed request. This method is intended for developers who
need to retrieve the signed request by using a more client-side JavaScript approach. (The Canvas
SDK sends the signed request to your app.)
repost Method
Requests the parent window to initiate a POST to your canvas app and reloads the app page with a
refreshed signed request. After the SAML SSO process is completed, your app can call this method
and a new signed request is sent to your app via a POST. This method is for developers who want to
retrieve the signed request using a more server-side approach. (Salesforce POSTs the signed request
to your server.)
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
OAuth & SSO Flow diagrams
IdP Initiated SAML SSO
Delegated authentication flow
1 1 1 1
P h o n e / W h a t s a p p :  +1 (515) 309-7846 (USA) E m a i l :  info@zarantech.com
www.zarantech.com
THANK YOU
P h o n e / W h a t s a p p :  +1 (515) 309-7846
E m a i l :  info@zarantech.com
www.zarantech.com
Corporate Training Course Catalog
https://bit.ly/salesforce-course-catalog
Salesforce Learner Community
https://www.linkedin.com/showcase/salesforce-learner-community/
Get any Salesforce Video Training
https://zarantech.teachable.com/courses/category/salesforce

