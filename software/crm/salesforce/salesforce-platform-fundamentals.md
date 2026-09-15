---
id: software/crm/salesforce/salesforce-platform-fundamentals
canonical_question: What is the core architecture, data model, sharing rules, and
  security model of Salesforce CRM?
aliases:
- Salesforce fundamentals guide
- Salesforce data model standard custom objects
- Salesforce role hierarchy and sharing rules
- Salesforce org security and profiles
- Salesforce Winter release features
entity_type: platform_handbook
domain: software > crm > salesforce
last_verified: '2026-09-15'
---

# Salesforce Platform Fundamentals: Data Model, Security, and Core CRM

## 1. Overview, Core Concepts & Scope

Get Started with Salesforce
Salesforce, Winter ’25
Last updated: August 23, 2024
© Copyright 2000–2024 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other
names and marks. Other marks appearing herein may be trademarks of their respective owners.
CONTENTS
Get Started with Salesforce . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
What Is Salesforce? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
Log In, Navigate, and Search Salesforce . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103
Verify Your Identity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 138
Personalize Your Salesforce Experience . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 174
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 265
GET STARTED WITH SALESFORCE
EDITIONS
Available in: Salesforce
Classic (not available in all
orgs)
Available in: all editions
Welcome to Salesforce, the award-winning cloud computing service designed to help you manage
your customer relationships, integrate with other systems, and build your own applications! Here
are some key concepts to help you understand the Salesforce products and editions and guide you
through common tasks in Salesforce.
What Is Salesforce?
Salesforce is your customer success platform, designed to help you sell, service, market, analyze,
and connect with your customers.
Log In, Navigate, and Search Salesforce
New to Salesforce? Learn how to navigate, customize, and manage basic CRM features.
Verify Your Identity
Use identity verification tools to secure and protect your data from unauthorized access.
Personalize Your Salesforce Experience
Update your personal information, for example your email address. Change your password and security question. If you have
administrator permissions, you can also customize your Salesforce org.
What Is Salesforce?
EDITIONS
Available in: both Lightning
Experience and Salesforce
Classic
Your Salesforce edition
determines which features
and functionality you can
access.
Salesforce is your customer success platform, designed to help you sell, service, market, analyze,
and connect with your customers.
Run your business from anywhere with Salesforce. Use standard products and features to manage
relationships with prospects and customers, collaborate and engage with employees and partners,
and store your data securely in the cloud.
But standard products and features are only the beginning. With our platform, you can customize
and personalize the experience for your customers, partners, and employees and easily extend
beyond out of the box functionality.
1
Concepts, Products, and Services
As you get started with Salesforce, it’s helpful to learn some key concepts and terms. They come up frequently when you interact
with the product, our documentation, and our service professionals. The concepts and terms here help you understand how Salesforce
works.
The Salesforce

---

## 2. Technical Architecture, Workflows & Operational Methodologies

’t see Setup in the header, click your name,
then select Setup.
134
Set Up Your Chatter ProfileGet Started with Salesforce
2. Enter the name of the Setup page, record, or object that you want in the Quick Find box, then select the appropriate page
from the menu.
Tip:  Type the first few characters of a page’s name in the Quick Find box. As you type, pages that match your search
terms appear in the menu. For example, to find the Language Settings page, type lang in the Quick Find box, then
select Language Settings.
View and Display FAQ
Common questions around popup windows, buttons, links, and other display elements on Salesforce pages.
What’s the Collapsible Sidebar?
The sidebar column that appears on the left side of most Salesforce pages in Salesforce Classic provides convenient access to links
and commands.
Why Can’t I See Some Features?
You learn about Salesforce features in our help documentation and training videos. However, sometimes you can’t seem to find or
access these features in your Salesforce org.
Why Can't I View Salesforce Popup Windows Such as Lookup Dialogs and Help Pages?
Test your browser’s popup blocker settings. If the settings are configured for maximum security, you can’t view any popup windows
within Salesforce, including popups that provide necessary functionality.
Why Can't I See Some Buttons and Links?
Buttons and links only display for users who have the appropriate permissions to use them.
Why Did My Data Disappear When I Pressed the Backspace Key While Editing a Record in Salesforce Classic?
Some versions of Internet Explorer use the Backspace key as a keyboard shortcut for the browser’s Back button. When you press the
Backspace key and your cursor is not within a text field, the browser goes back to the previous page. To retrieve your data and return
to the page you were working on, click your browser’s Forward button.
Can I Change or Delete the List of Entries That Appears When I Edit a Text Field in Salesforce Classic?
No. These auto-complete entries that appear when you are editing certain text fields are a feature of Internet Explorer.
Why Am I Getting an Error Message?
When you’re working in Salesforce, you can occasionally get an error message. Typically, an error message appears when you try to
view, edit, or delete information to which you don't have access.
What’s the Collapsible Sidebar?
EDITIONS
Available in: Salesforce
Classic (not available in all
orgs)
Available in: all editions
except Database.com
The sidebar column that appears on the left side of most Salesforce pages in Salesforce Classic
provides convenient access to links and commands.
Click the edge of the sidebar to open or close the sidebar as needed.
135
View and Display FAQGet Started with Salesforce
The options in your sidebar vary depending on the features that are available in your org and whether your administrator has customized
the page layout.
Why Can’t I See Some Features?
EDITIONS
Available in: both Salesforce
Classic (not available in all
orgs) and Lightning
Experience
Available in: All editions
You learn about Salesforce features in our help documentation and training videos. However,
sometimes you can’t seem to find or access these features in your Salesforce org.
Here are some reason why you can’t find or access a particular feature or object.
• You don’t have the required permissions and access settings
• Your company renamed some standard objects and fields or created their own custom objects
and fields
• The feature you’re looking for isn’t included in your company’s Salesforce edition or Salesforce
experience
• You have to first adjust your custom page views or install external apps to enable the feature
Why Can't I View Salesforce Popup Windows Such as Lookup Dialogs and Help Pages?
Test your browser’s popup blocker settings. If the settings are configured for maximum security, you can’t view any popup windows
within Salesforce, including popups that provide necessary functionality.
For example, maximum security settings block calendar popup for choosing a date on an activity, lookup dialogs for selecting a record,
and Help pages.
To allow popup windows for Salesforce, add Salesforce as a trusted site within your browser's popup blocker settings. Consult the help
for your browser for specific instructions.
Some browser add-ons, like the Google toolbar, also have popup blocking. Consult your software documentation on those products for
details on how to configure them to allow popup windows fro

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

features on a continuous basis, outside of our normal release
cycle.
What features are available?
The initial release of the Lightning Extension contains these new features.
• The Component Customization feature (Beta) lets you declutter record and home pages by hiding components with the
icon
in the header.
• The Link Grabber feature (Beta) makes all Lightning links open in a single browser tab.
I only want my users to have access to certain features. Can I disable some of the
features offered in the Lightning Extension?
Yes. To disable features, from Setup, in the Quick Find box, enter Lightning Extension, and then select Lightning Extension.
From there, you can control access to individual features, or access to the extension itself. Changes can take up to 24 hours to take effect.
Component Customization (Beta) FAQ
Hide components in home and record pages on a per-app basis.
Link Grabber (Beta) FAQ
Save time every time you open a Lightning link. Makes all Lightning links open in a single browser tab.
SEE ALSO:
External Link: Download the Lightning Extension from the Chrome Web Store
Component Customization (Beta) FAQ
Link Grabber (Beta) FAQ
Component Customization (Beta) FAQ
Hide components in home and record pages on a per-app basis.
This feature is a Beta Service. Customer may opt to try such Beta Service in its sole discretion. Any use of the Beta Service is subject to
the applicable Beta Services Terms provided at Agreements and Terms
262
Try New Features with the Lightning Extension for ChromeGet Started with Salesforce
How do I use the Component Customization (Beta) feature?
Click
on the header to edit a record or home page. To hide a component, select the component you want to hide, and click the
Component Visibility toggle in the customization panel.
SEE ALSO:
Try New Features with the Lightning Extension for Chrome
External Link: Download the Lightning Extension from the Chrome Web Store
Link Grabber (Beta) FAQ
Save time every time you open a Lightning link. Makes all Lightning links open in a single browser tab.
This feature is a Beta Service. Customer may opt to try such Beta Service in its sole discretion. Any use of the Beta Service is subject to
the applicable Beta Services Terms provided at Agreements and Terms
How does the Link Grabber (Beta) work?
The Link Grabber (Beta) takes all Lightning links and opens them in a single browser tab. For standard navigation apps, this means that
the content that’s currently open in your app is replaced with the content from the link. For Lightning console apps, that means that
the link opens in a new workspace tab in your current console session.
263
Try New Features with the Lightning Extension for ChromeGet Started with Salesforce
Is this feature related to the Lightning Console Extension?
The Lightning Console Extension is the standalone version of the Link Grabber (Beta). Turning on the Link Grabber (Beta) automatically
disables the Lightning Console Extension. If you continue to use the Link Grabber (Beta) feature, we recommend uninstalling the Lightning
Console Extension.
SEE ALSO:
Try New Features with the Lightning Extension for Chrome
External Link: Download the Lightning Extension from the Chrome Web Store
264
Try New Features with the Lightning Extension for ChromeGet Started with Salesforce
INDEX
A
Assistant
Lightning Experience
192
assistant 192
K
Keyboard shortcuts
in Salesforce Classic 77
S
Salesforce administrator
can’t see features 136
Setup
user 174, 180, 191
265

