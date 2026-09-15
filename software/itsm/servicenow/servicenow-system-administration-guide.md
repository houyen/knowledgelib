---
id: software/itsm/servicenow/servicenow-system-administration-guide
canonical_question: How are user roles, Access Control Lists (ACLs), UI policies,
  and client scripts configured in ServiceNow?
aliases:
- ServiceNow admin tutorial
- ServiceNow ACLs security rules
- UI policies vs client scripts ServiceNow
- ServiceNow update sets migration
- ServiceNow reporting and dashboards
entity_type: administration_guide
domain: software > itsm > servicenow
last_verified: '2026-09-15'
---

# ServiceNow System Administration: User Roles, ACLs, and Service Portal Configuration

## 1. Overview, Core Concepts & Scope

One Identity Safeguard for Privileged
Sessions 7.1
ServiceNow - Tutorial
Copyright 2022 One Identity LLC.
ALL RIGHTS RESERVED.
This guide contains proprietary information protected by copyright. The software described in this
guide is furnished under a software license or nondisclosure agreement. This software may be used
or copied only in accordance with the terms of the applicable agreement. No part of this guide may
be reproduced or transmitted in any form or by any means, electronic or mechanical, including
photocopying and recording for any purpose other than the purchaser’s personal use without the
written permission of One Identity LLC .
The information in this document is provided in connection with One Identity products. No license,
express or implied, by estoppel or otherwise, to any intellectual property right is granted by this
document or in connection with the sale of One Identity LLC products. EXCEPT AS SET FORTH IN THE
TERMS AND CONDITIONS AS SPECIFIED IN THE LICENSE AGREEMENT FOR THIS PRODUCT,
ONE IDENTITY ASSUMES NO LIABILITY WHATSOEVER AND DISCLAIMS ANY EXPRESS, IMPLIED OR
STATUTORY WARRANTY RELATING TO ITS PRODUCTS INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-
INFRINGEMENT. IN NO EVENT SHALL ONE IDENTITY BE LIABLE FOR ANY DIRECT, INDIRECT,
CONSEQUENTIAL, PUNITIVE, SPECIAL OR INCIDENTAL DAMAGES (INCLUDING, WITHOUT
LIMITATION, DAMAGES FOR LOSS OF PROFITS, BUSINESS INTERRUPTION OR LOSS OF
INFORMATION) ARISING OUT OF THE USE OR INABILITY TO USE THIS DOCUMENT, EVEN IF
ONE IDENTITY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. One Identity makes
no representations or warranties with respect to the accuracy or completeness of the contents of this
document and reserves the right to make changes to specifications and product descriptions at any
time without notice. One Identity does not make any commitment to update the information
contained in this document.
If you have any questions regarding your potential use of this material, contact:
One Identity LLC.
Attn: LEGAL Dept
4 Polaris Way
Aliso Viejo, CA 92656
Refer to our Web site (http://www.OneIdentity.com) for regional and international office
information.
Patents
One Identity is proud of our advanced technology. Patents and pending patents may apply to this
product. For the most current information about applicable patents for this product, please visit our
website at http://www.OneIdentity.com/legal/patents.aspx.
Trademarks
One Identity and the One Identity logo are trademarks and registered trademarks of One Identity
LLC. in the U.S.A. and other countries. For a complete list of One Identity trademarks, please visit
our website at www.OneIdentity.com/legal/trademark-information.aspx.  All other trademarks are
the property of their respective owners.
Legend
WARNING: A WARNING icon highlights a potential risk of bodily injury or property
damage, for which industry-standard safety precautions are advised. This icon is
often associated with electrical hazards related to hardware.
CAUTION: A CAUTION icon indicates potential damage to hardware or loss of data
if instructions are not followed.
SPSServiceNow -

---

## 2. Technical Architecture, Workflows & Operational Methodologies

e [service_now_ticket_patterns] section of the plugin to
perform a query on the ServiceNow server. During authentication, SPS prompts the user
for a valid ServiceNow ticket ID, and if the result of the query defined in the [service_now_
ticket_patterns] section and the ticket ID entered by the user match, SPS permits the user
access to the information system.
You can define more than one ServiceNow ticket patterns for different ServiceNow task
types,  for example, one for an incident (INC), one for a change request (CHG), and another
one for a problem (PRB), and so on. Every defined ServiceNow ticket pattern must have a
corresponding section, that is, if you define a ServiceNow ticket pattern, for example, for
an  incident (INC), you must also define a corresponding the ticket pattern section for the
incident (INC), which also includes the  table and query options.
[service_now_ticket_patterns]
[ServiceNow task type]=[task_type_].*
table=
query=
ServiceNow task type
Type:         string
Required:         yes
Default:         N/A
Description: Specifies the  ServiceNow task type,  for example,  incident (INC),  change
request (CHG), problem (PRB), or any other custom defined task type in ServiceNow. SPS
uses the task type you define for the ticket pattern to filter in ServiceNow and list all the
relevant task types. For example, for an incident task type, enter incident=INC.* as the
[ServiceNow task type]=[task_type].* section and during authorization, SPS filters all
the tasks beginning with INC in ServiceNow.
table
Type:          string
Required:          yes
Default:          N/A
Description: The table in ServiceNow where your ServiceNow task type is stored in the
database. For example, for an incident task type, specify the table in which incidents are
stored. To do this, in ServiceNow find the table, which includes the required task type as
shown in the example below:
SPS7.1ServiceNow-Tutorial
SPSServiceNowpluginparameterreference
19
1. In ServiceNow, filter for tables, and select Tables.
Figure 2: Filter for tables
2. From the list of Tables, narrow your search to find the required task type, then click
the task type.
Figure 3: Example filtering on the Incident task type
3. Copy the Name field, which in this example is incident, and paste it in the table=
section of     your ServiceNow plugin.
Figure 4: Copy Name field
SPS7.1ServiceNow-Tutorial
SPSServiceNowpluginparameterreference
20
query
Type:          string
Required:          yes
Default:          N/A
Description: The query SPS  runs in ServiceNow to validate the ServiceNow ticket ID.
1. In ServiceNow, filter for the required task type view. For example, for an incident
task type, enter Incident or INC*.
Figure 5: Filter for task type view
2. Create a filter by adding as many conditions as required.
Figure 6: Add conditions to your filter
3. When your filter is ready, run your filter.
4. Copy the filter you defined. Right-click the last element of your filter, and
select Copy query.
SPS7.1ServiceNow-Tutorial
SPSServiceNowpluginparameterreference
21
Figure 7: Copy your filter
5. Paste the filter you copied in the query= section of  your ServiceNow plugin.
[auth]
This section contains the options related to authentication.
Declaration
[auth]
prompt=Press Enter for push notification or type one-time password:
disable_echo=yes
prompt
Type:         string
Required:        no
Default:        Press Enter for push notification or type one-time password:
Description: SPS displays this text to the user in a terminal connection to request an OTP
interactively. The text is displayed only if the user uses an OTP-like factor, and does not
send the OTP in the connection request.
disable_echo
Type:         boolean (yes|no)
Required:         no
Default:         no
SPS7.1ServiceNow-Tutorial
SPSServiceNowpluginparameterreference
22
Description: For better security, you can hide the characters (OTP or password) that the
user types after the prompt. To hide the characters (replace them with asterisks), set
disable_echo to yes.
[connection_limit by=client_ip_
gateway_user]
This section contains the options related to limiting parallel sessions.
Declaration
[connection_limit by=client_ip_gateway_user]
limit=0
limit
Type: integer
Required:         no
Default:         0
Description: To limit the number of parallel sessions the gateway user can start from a
given client IP address, configure limit. For an unlimited number of sessions, type 0.
[authentication_cache]
This section conta

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

before the regular content (for example, your username) of the field.
If you can authenticate using an OTP or token, encode the OTP as part of the
username. To encode additional data, you can use the following special characters:
l % as a field separator
l ~ as the equal sign
l ^ as a colon (for example, to specify the port number or an IPv6 IP address)
Example:
For example, use the following format:
domain\otp~YOUR-ONE-TIME-PASSWORD%Administrator
Replace YOUR-ONE-TIME-PASSWORD with your actual OTP.
3. Connect to the server.
If you need to authenticate using a push notification, approve the connection in your
mobile app.
4. Authenticate on the server.
5. If authentication is successful, you can access the server.
SPS7.1ServiceNow-Tutorial
Performmulti-factorauthenticationwiththeSPSplugininRemote
Desktop(RDP)connections
37
Perform multi-factor authentication
with the SPS  plugin in Microsoft SQL
Server (MSSQL) connections
The following section describes how to establish a Microsoft SQL Server (MSSQL)
connection to a server when the AA plugin is configured.
To establish a MSSQL connection to a server when the AA plugin is configured
1. Open your SQL client application.
2. If you have to provide additional information to authenticate on the server, you must
enter this information in your SQL client application in the User name field, before the
regular content (for example, your username) of the field.
If you can authenticate using an OTP or token, encode the OTP as part of the
username. To encode additional data, you can use the following special characters:
l % as a field separator
l ~ as the equal sign
l ^ as a colon (for example, to specify the port number or an IPv6 IP address)
Example:
For example, use the following format:
domain\otp~YOUR-ONE-TIME-PASSWORD%Administrator
Replace YOUR-ONE-TIME-PASSWORD with your actual OTP.
3. Connect to the server.
If you need to authenticate using a push notification, approve the connection in your
mobile app.
4. Authenticate on the server.
5. If authentication is successful, you can access the server.
SPS7.1ServiceNow-Tutorial
Performmulti-factorauthenticationwiththeSPSplugininMicrosoft
SQLServer(MSSQL)connections
38
Aboutus
About us
One Identity solutions eliminate the complexities and time-consuming processes often
required to govern identities, manage privileged accounts and control access. Our solutions
enhance business agility while addressing your IAM challenges with on-premises, cloud and
hybrid environments.
SPS7.1ServiceNow-Tutorial
Aboutus
39
Contacting us
For sales and other inquiries, such as licensing, support, and renewals, visit
https://www.oneidentity.com/company/contact-us.aspx.
SPS7.1ServiceNow-Tutorial
Contactingus
40
Technical support resources
Technical support is available to One Identity customers with a valid maintenance contract
and customers who have trial versions. You can access the Support Portal at
https://support.oneidentity.com/.
The Support Portal provides self-help tools you can use to solve problems quickly and
independently, 24 hours a day, 365 days a year. The Support Portal enables you to:
l Submit and manage a Service Request
l View Knowledge Base articles
l Sign up for product notifications
l Download software and technical documentation
l View how-to videos at www.YouTube.com/OneIdentity
l Engage in community discussions
l Chat with support engineers online
l View services to assist you with your product
SPS7.1ServiceNow-Tutorial
Technicalsupportresources
41

