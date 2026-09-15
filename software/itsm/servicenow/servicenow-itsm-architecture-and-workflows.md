---
id: software/itsm/servicenow/servicenow-itsm-architecture-and-workflows
canonical_question: How does ServiceNow implement IT Service Management (ITSM), Configuration
  Management (CMDB), and workflow automation?
aliases:
- ServiceNow ITSM tutorial
- ServiceNow incident problem change management
- ServiceNow CMDB configuration items
- ServiceNow service catalog workflows
- ServiceNow table structure and business rules
entity_type: platform_tutorial
domain: software > itsm > servicenow
last_verified: '2026-09-15'
---

# ServiceNow ITSM Architecture: Incident, Problem, Change, and CMDB Workflows

## 1. Overview, Core Concepts & Scope

ServiceNow
i
A
ServiceNow
ii
About the T utorial
ServiceNow is a cloud solution company which is used for process automation, IT service
management, IT operation management and IT business management. At the end of this
tutorial, you should have gained good knowledge in ServiceNow ad ministration and
development.
Audience
This tutorial is designed for readers who are interested in understanding the concepts of
ServiceNow. The tutorial also covers the basics of IT service management (ITSM) and
Cloud computing. It is mainly targeted fo r software professionals who are involved in
ServiceNow administration and its development.
Prerequisites
This is an elementary tutorial which will help you to understand the concepts of ServiceNow
from scratch. There is no prior knowledge required to lea rn ServiceNow administration,
but for ServiceNow development, knowledge of Javascript is mandatory. It will be good to
have some basic understanding of ITSM, however, not mandatory.
Copyright & Disclaimer
 Copyright 2020 by Tutorials Point (I) Pvt. Ltd.
All the content and graphics published in this e-book are the property of Tutorials Point (I)
Pvt. Ltd.  The user of this e-book is prohibited to reuse, retain, copy, distribute or republish
any contents or a part of contents of this e -book in any manner w ithout written consent
of the publisher.
We strive to update the contents of our website and tutorials as timely and as precisely as
possible, however, the contents may contain inaccuracies or errors. Tutorials Point (I) Pvt.
Ltd. provides no guarantee r egarding the accuracy, timeliness or completeness of our
website or its contents including this tutorial. If you discover any errors on our website or
in this tutorial, please notify us at contact@tutorialspoint.com
ServiceNow
iii
T able of Contents
About the Tutorial ........................................................................................................................................... ii
Audience .......................................................................................................................................................... ii
Prerequisites .................................................................................................................................................... ii
Copyright & Disclaimer .................................................................................................................................... ii
Table of Contents ........................................................................................................................................... iii
1. ServiceNow ― Introduction ...................................................................................................................... 1
Services of ServiceNow .................................................................................................................................... 1
ServiceNow Instance ....................................................................................................................................... 2
Generating Developer Instance ..........................................................................

---

## 2. Technical Architecture, Workflows & Operational Methodologies

M guided setup, search ITSM in the navigation
bar and open the first search result “ITSM guided setup” and click on the Get started
button, as shown below.
5. ServiceNow — Administration
ServiceNow
30
The entire setup is organised into categories like Company, Connectivity, Foundational
data, CMDB, etc. We have to configure each category one by one using an interactive and
guided menu. The completion progress for each category is displayed, beside the content
frame and also, the overall completion status is displayed at the top of content frame.
We can configure the catego ry in any order and we can skip the configuration of any
specific category as well. The task for the configuration of the ServiceNow from scratch is
very big and, therefore, we can assign the task to configure each category to the individual
admin user.
The steps in guided setup are very detailed and self-explanatory. You can play around with
the guided setup and try to configure the various categories. There are instructions and
help available in every category for the reference.
ServiceNow
31
Import sets
The import sets are used to import the data in ServiceNow from external sources like
excel, JDBC, etc. The data is imported in the ServiceNow and then, mapped in the relevant
ServiceNow tables. The data can be imported manually one time, or we can schedule the
periodic import to happen automatically. Let’s discuss, both the imports one by one with
the help of an example.
Manual Import
The data can be imported manually using the “Load data” module of “System import set”
application. Let’s take an example, we have to import 5 groups in ServiceNow. The table,
which stores the group in the ServiceNow is sys_user_group. To browse the data in this
table, simply type “sys_user_group.list” in the navigation bar.
Suppose, we have data of five groups in the excel, which we w ant to upload in the
ServiceNow.
Open the “Load data” module for “System import set” application. In the import set table,
click on the “Create table”, as we do not have any existing import table for importing user
groups. The import tables are basically the intermediate tables or the staging table.
ServiceNow
32
As we import the file, the data is first loaded in this table and then, we can load the data
from this import table to the actual target table in the ServiceNow (sys_user_group in this
case).
Then, give the name of the new table in the Label field. The important point to note here,
is all the tables, which are created by the user, have the prefix of “u_” in the name and all
the system tables of ServiceNow have prefix “sys_” in the name.
Select the file from the explorer. Additionally, you can give the sheet number, which
corresponds to the tab in the excel and header row (column name) in the excel. Both of
them are “1” in our case. Finally, click on submit.
Once the process is complete, you will see th e above screen with state as complete and
the next steps which have to be followed. First, let us go to the Import Sets under Next
steps.
You can see that the import set has been created with the state as “Loaded”, which means
that the data in our excel file, has been loaded in our intermediate table
ServiceNow
33
“u_user_group_import”.  You can check the data in this intermediate table, by searching
u_user_group_import.list in the navigation bar.
Now let's move ahead and create a transform map for this imported data. In the transform
map, basically, we create the mapping between intermediate table and target table
(sys_user_group system table), that means which column of intermediate table
corresponds to which column of target table, so that data can be loaded in ta rget table
accordingly.
Go to the “Create transform map” module under the “System import set” application and
give any name for the transform map. Select the source table, which is
u_user_group_import in our case and the target table, which is sys_user_goup. Since, we
have to keep this transform map active, check the active box and check “Run business
rule” as well. The business rules are a set of rules, which runs when any insert or update
is made on the table.
For example, if a user does not enter any d ata in a field, the default values are set
automatically. You can even give your own script, if you want to process the data before
inserting it to target table, for this check the Run script box.
Now, that we have created a transform map, either we ca n map the column of source
table to target table, or allow Serv

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

scripts
The best way to debug the client script is referring to logs. The Javascript provides jslog()
method to write messages in Javascript logs. The jslog() method accepts messages, which
we want in the logs in the argument. Below is an example on, how we can implement the
jslog(). You can use the below script in the business rule script.
function onLoad(){
jslog("This log is displayed from jslog().");
jslog("The value of Member field is = " + g_form.getValue('Member'));
}
This will give the value given in the member field in the logs. In this case, we have used
the getvalue method, to retrieve the value of the member field.  Now, the next step is to
turn the logs on. Go to setting option on the top right corner and cli ck on developer tab.
Turn on the “Javascript log and Field watcher” option.
The JavaScript Logs will open in a new section at the bottom of the main ServiceNow
browser window.
ServiceNow
73
Apart from jslog() we can also use try/catch statements which we general ly use in
Javascript to debug the scripts.
Debugging server side script
The most common way of debugging server side script is using “Script debugger” module.
The script debugger can be used to place breakpoints, traverse the code step by step,
view value  of variables, etc. To access script debugger, find “script debugger” in the
navigation bar. It is present inside “System Diagnostics” application.
Apart from this, we can also refer to “Application logs” module, which is present inside
“System log application”.
ServiceNow
74
ServiceNow is an enterprise cloud ecosystem, which has revolutionised the way ITSM is
implemented within the organisation. Due to its flexibility, better quality, improved
productivity and easy integration, it is in very much demand.
Our ServiceNow tutorial, should have given you a strong base and sufficient knowledge to
start your journey as a ServiceNow professional. You can start creating new applications
in your developer instances, for hypothetical use cases, because hands on is very
necessary, to grasp each and every topic and to build good understanding on each topic.
You have two career options in the field of ServiceNow, which are as follows:
 ServiceNow developer
 ServiceNow administrators
Although having a specialisation in administration or development is very beneficial. Many
organisations prefer to hire resources having knowledge of both fields. We have tried to
cover the important concepts of both administration and development in this tutorial.
However, you can gain more proficienc y by going through ServiceNow documentations.
ServiceNow has organised the documentation of their products very systematically and
you can refer to it, using this link https://docs.servicenow.com/ .
Next thing, we want to highlight is that, you can showcase your ServiceNow skills through
ServiceNow certification. To earn a ServiceNow certification, it is mandatory to complete
the ServiceNow paid training first and post which, you will receive a free certifica tion
voucher.
ServiceNow have divided the certifications in four main categories, which are as follows:
 Certified implementation specialist (CIS)
 Certified application developer (CAD)
 Certified application specialist (CAS)
 Certified system administrator (CSA)
You can find more details on ServiceNow certifications and ServiceNow authorised training
partners on this URL, https://www.servicenow.com/services/training-and-
certification.html
7. ServiceNow — Mastering and Certification

