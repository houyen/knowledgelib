---
id: software/crm/salesforce/salesforce-developer-and-admin-handbook
canonical_question: How are Apex code, SOQL queries, triggers, and workflow automations
  built in Salesforce?
aliases:
- Salesforce developer handbook
- Apex triggers and governor limits
- SOQL query syntax
- Lightning Web Components LWC
- Salesforce Process Builder Flow
entity_type: developer_handbook
domain: software > crm > salesforce
last_verified: '2026-09-15'
---

# Salesforce Developer & Administrator Handbook: Apex, SOQL, and Automation

## 1. Overview, Core Concepts & Scope

Salesforce
#salesforce
Table of Contents
About 1
Chapter 1: Getting started with Salesforce 2
Remarks 2
Examples 2
Installation or Setup 2
Salesforce Products 2
Sales Cloud 2
Service Cloud 2
Marketing Cloud 2
Community Cloud 2
Analytics Cloud aka Wave Analytics 2
App Cloud 3
IoT Cloud 3
Industry Specific Products 3
Financial Services Cloud 3
Health Cloud 3
Heroku 3
Chapter 2: Apex Testing 4
Examples 4
Assert Methods 4
Basic Test Class 4
Using testSetup 5
Using static blocks 5
Assertion Methods 6
Chapter 3: Apex Triggers 7
Syntax 7
Parameters 7
Examples 7
Basic trigger 7
Trigger context variables 7
Manipulating records that fired the trigger 8
Chapter 4: Approval Process Objects 10
Remarks 10
Examples 11
ProcessDefinition 11
ProcessNode 12
ProcessInstance 12
ProcessInstanceStep & ProcessInstanceWorkitem 12
ProcessInstanceHistory* 13
Chapter 5: Custom Settings 14
Remarks 14
Introduction 14
List Custom Settings 14
Examples 15
Creating & Managing Custom Settings 15
Creation 15
Management 15
Using Hierarchy Custom Settings To Disable Workflow / Validation Rules 16
Custom Setting 16
Custom Setting Field 17
Custom Setting Field Value 17
Validation Rule 18
Workflow Rules 19
Using Hierarchy Custom Settings To Disable Apex Code 19
Explanation 19
Apex Class 19
Unit Test 19
Updating Hierarchy Custom Settings in Apex Code 21
Chapter 6: Date Time Manipulation 26
Examples 26
Easily Find Last Day of a Month 26
Chapter 7: Global Variables in classes 27
Introduction 27
Examples 27
UserInfo 27
Chapter 8: Global Variables on Visualforce pages 28
Examples 28
$Resource 28
$Label 28
$User 28
Chapter 9: Page Navigation with help of list wrapper class in sales force. 29
Introduction 29
Examples 29
Pagination Controller 29
Chapter 10: SalesForce CI Integration 33
Introduction 33
Examples 33
How to configure Jenkins to deploy code on Development or Production org ? 33
Jenkins CI tools which can be used for SalesForce Automation 33
Chapter 11: Salesforce Object Query Language (SOQL) 34
Syntax 34
Examples 34
Basic SOQL Query 34
SOQL Query With Filtering 34
SOQL Query With Ordering 35
Using SOQL to Construct a Map 35
SOQL Query to Reference Parent Object's Fields 35
SOQL Queries in Apex 36
Variable References in Apex SOQL Queries 36
Potential Exceptions in Apex SOQL Queries 36
Using a Semi-Join 37
Dynamic SOQL 37
Chapter 12: Salesforce REST API 38
Introduction 38
Examples 38
OAuth2 access_token and list of services 38
Chapter 13: Tools for Development 39
Examples 39
IDEs 39
Browser extensions 39
Debuggers 39
Salesforce ETL tools 40
Static Analysis Tools 40
Chapter 14: Trigger Bulkification 41
Examples 41
Bulkification 41
Chapter 15: Visualforce Page Development 42
Examples 42
Basic page 42
Using Standard Controllers 42
Chapter 16: Working with External Systems 43
Examples 43
Making an outbound callout 43
Credits 44
About
You can share this PDF with anyone you feel could benefit from it, downloaded the latest version
from: salesforce
It is an unofficial and free Salesforce ebook created for educational purposes. All the content is
extracted from Stack Overflow Documentation, which is written by many hardworking individuals at
Stack Overflow. It is neither affiliated with S

---

## 2. Technical Architecture, Workflows & Operational Methodologies

ator' LIMIT 1];
User u = new User(LastName = 'Test',Alias = 't1',Email = 'example@gmail.com',Username
= 'sotest@gmail.com',ProfileId = p.Id,TimeZoneSidKey = 'America/Denver',LocaleSidKey =
'en_US',EmailEncodingKey = 'UTF-8',LanguageLocaleKey = 'en_US');
insert u;
Val_Rule_Cntrlr__c valRuleCntrlr = new Val_Rule_Cntrlr__c(SetupOwnerId =
u.Id,All_Opportunity_Disabled__c = false);
https://riptutorial.com/ 22
upsert valRuleCntrlr;
List<Opportunity> testOpps = new List<Opportunity>();
// create the Opportunities that will be updated by the class
for(integer i = 0; i < 200; i++) {
testOpps.add(new Opportunity(
Name          = 'Test Opp Update' + i,
OwnerId       = u.Id,
StageName     = 'Prospecting',
CloseDate     = date.today().addDays(1),
Amount        = 100,
// set checkbox field to true, to trigger validation rules if they've not been
deactivated by class
Trigger_Validation_Rule__c = true));
}
// create the Opportunities that won't be updated by the class
for(integer i = 0; i < 200; i++) {
testOpps.add(new Opportunity(
Name          = 'Test Opp Skip' + i,
OwnerId       = u.Id,
StageName     = 'Prospecting',
CloseDate     = date.today().addDays(15),
Amount        = 100,
Trigger_Validation_Rule__c = true));
}
insert testOpps;
}
// code required to test a scheduled class, see
https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_scheduler.htm
for more details
public static String CRON_EXP = '0 0 0 15 3 ? 2022';
static testmethod void testCloseDateUpdates() {
// execute scheduled class
Test.startTest();
String jobId = System.schedule('ScheduleApexClassTest',
CRON_EXP,
new Scheduled_OppCloseDateUpdate());
CronTrigger ct = [SELECT Id, CronExpression, TimesTriggered, NextFireTime
FROM CronTrigger
WHERE id = :jobId];
System.assertEquals(CRON_EXP, ct.CronExpression);
System.assertEquals(0, ct.TimesTriggered);
System.assertEquals('2022-03-15 00:00:00', String.valueOf(ct.NextFireTime));
Test.stopTest();
// test results
Integer updateCount = 0;
Integer skipCount   = 0;
List <Opportunity> opportunitys = [SELECT Id, Name, CloseDate FROM Opportunity];
https://riptutorial.com/ 23
for(Opportunity o : opportunitys) {
if (o.Name.contains('Update') &&
updateCount == 0)
{
System.assertEquals(date.today().addDays(20), o.CloseDate, 'Opportunity\'s
Close Date should have been updated as it was less than 7 days away');
updateCount = 1;
}
if (o.Name.contains('Skip') &&
skipCount == 0)
{
System.assertEquals(date.today().addDays(15), o.CloseDate, 'Opportunity should
not have been updated as it\'s Close Date is more than 7 days away');
skipCount = 1;
}
}
// check that both lists of Opportunities have been tested
System.assertEquals(2, updateCount + skipCount, 'Count should be 2 once all assertions
have been executed');
}
// check that the class does not change the custom setting's field to false, if it was
true before class was executed
static testmethod void testSettingUpdates() {
User u = [SELECT Id FROM User WHERE UserName = 'sotest@gmail.com'];
// switch the custom setting field to true before the scheduled job executes
Val_Rule_Cntrlr__c setting;
setting = Val_Rule_Cntrlr__c.getInstance(u.Id);
setting.All_Opportunity_Disabled__c = true;
upsert setting;
System.runAs(u) {
Test.startTest();
String jobId = System.schedule('ScheduleApexClassTest',
CRON_EXP,
new Scheduled_OppCloseDateUpdate());
CronTrigger ct = [SELECT Id, CronExpression, TimesTriggered, NextFireTime
FROM CronTrigger
WHERE id = :jobId];
System.assertEquals(CRON_EXP, ct.CronExpression);
System.assertEquals(0, ct.TimesTriggered);
System.assertEquals('2022-03-15 00:00:00', String.valueOf(ct.NextFireTime));
Test.stopTest();
}
setting = Val_Rule_Cntrlr__c.getInstance(u.Id);
// check that the class did not change the All_Opportunity_Disabled__c field to false
System.assertEquals(true, setting.All_Opportunity_Disabled__c);
}
}
https://riptutorial.com/ 24
Read Custom Settings online: https://riptutorial.com/salesforce/topic/4927/custom-settings
https://riptutorial.com/ 25
Chapter 6: Date Time Manipulation
Examples
Easily Find Last Day of a Month
If you need to find the last day of the month, you can do complicated DateTime gymnastics or you
can use the following method.
Say you want to find the last day of February 2021. Do the following:
Integer month = 2;
Integer day = null;
Integer year = 2021;
// Create a new DateTime object for the first day of the month following
// the date you're looking for.
DateTime dtTarget = DateTime.newInstance(year, month, 1);
//In this

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

e/topic/4272/trigger-bulkification
https://riptutorial.com/ 41
Chapter 15: Visualforce Page Development
Examples
Basic page
A basic VisualForce page can be created like this:
<apex:page>
<h1>Hello, world!</h1>
</apex:page>
Using Standard Controllers
If your page is for displaying or editing information about a particular type of record, it may be
helpful to use a standard controller to reduce the amount of boilerplate code you need to write.
By using a standard controller, your page will be displayed with an ?id=SALESFORCE_ID parameter,
and you automatically get access to all merge fields on the record.
Add a standard controller to your page by specifying the standardController attribute on
<apex:page>:
<apex:page standardController="Account">
This is a page for {!Account.Name}
</apex:page>
You also get the standard controller methods for free:
cancel() - returns the PageReference for the cancel page (usually navigates back to a list view)•
delete() - deletes the record and returns the PageReference for the delete page•
edit() - returns the PageReference for the standard edit page•
save() - saves the record and returns the PageReference to the updated record•
view() - returns the PageReference for the standard view page•
You can use them like this:
<apex:page standardController="Account">
Name: <apex:inputField value="{!Account.Name}" />
<apex:commandButton value="Update record" action="{!save}" />
</apex:page>
Read Visualforce Page Development online:
https://riptutorial.com/salesforce/topic/6372/visualforce-page-development
https://riptutorial.com/ 42
Chapter 16: Working with External Systems
Examples
Making an outbound callout
This is an example on how to call a web service from salesforce. The code below is calling a
REST based service hosted on data.gov to find farmers markets close to the zipcode.
Please remember in order to invoke a HTTP callout from your org, you need to tweak the remote
settings for the org.
string url= 'http://search.ams.usda.gov/farmersmarkets/v1/data.svc/zipSearch?zip=10017';
Http h = new Http();
HttpRequest req = new HttpRequest();
HttpResponse res = new HttpResponse();
req.setEndpoint(url);
req.setMethod('GET');
res = h.send(req);
System.Debug('response body '+res.getBody());
Read Working with External Systems online: https://riptutorial.com/salesforce/topic/4926/working-
with-external-systems
https://riptutorial.com/ 43
Credits
S.
No Chapters Contributors
1 Getting started with
Salesforce abhi, Alex S, Andrii Muzychuk, Ashwani, Community, Reshma
2 Apex Testing Andree Wille, battery.cord, Ben, Eric Dobbs
3 Apex Triggers kurunve, Pedro Otero
4 Approval Process
Objects Ajay Gupta
5 Custom Settings Alex S
6 Date Time
Manipulation kurunve, LDP , RamenChef
7 Global Variables in
classes Andrii Muzychuk
8 Global Variables on
Visualforce pages Ben
9
Page Navigation with
help of list wrapper
class in sales force.
NITHESH K
10 SalesForce CI
Integration Sanjay Kharwar
11
Salesforce Object
Query Language
(SOQL)
abhi, Alex S, Andrii Muzychuk, battery.cord, Ben, ca_peterson,
Doug B, Eric Dobbs, LDP , Ratan Paul
12 Salesforce REST
API radbrawler
13 Tools for
Development
abhi, Andrii Muzychuk, Daniel Ballinger, Force2b, Gres, hleb not
bread, itzmukeshy7, Mahmood , NSjonas, Pavel Slepiankou,
pchittum, Ratan Paul, sorenkrabbe, wintermute
14 Trigger Bulkificationabhi, hillary.fraley, LDP
15 Visualforce Page
Development Ben
https://riptutorial.com/ 44
16 Working with
External Systems abhi, mnoronha
https://riptutorial.com/ 45

