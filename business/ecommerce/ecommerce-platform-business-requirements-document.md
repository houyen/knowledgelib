---
id: business/ecommerce/ecommerce-platform-business-requirements-document
canonical_question: What functional and non-functional requirements (product catalog,
  checkout, security, SEO) constitute an enterprise e-commerce BRD?
aliases:
- BRD ecommerce specification
- ecommerce functional requirements
- shopping cart checkout workflow BRD
- inventory sync payment requirements
- ecommerce user stories and acceptance criteria
entity_type: requirements_specification
domain: business > ecommerce
last_verified: '2026-09-15'
---

# E-Commerce Website & Platform Business Requirement Document (BRD) Specification

## 1. Overview, Core Concepts & Scope

Business Requirement Document: Ecommerce Website
Online Apparels shopping Website
Business Requirements Document (BRD)
Ecommerce Website
June 2019
Version 1.0
Page 7
1 Document Revisions
2 Approvals
Role Name Title Signature Date
Project Sponsor
Business Owner
Project Manager
System Architect
Development Lead
User Experience Lead
Quality Lead
Content Lead
Date Version Number Document Changes
13/06/2019 1.0 Initial Draft
Page 4
3 Introduction
3.1  Project Summary
3.1.1 Objectives
 Enhancing client’s offline business of apparels by transforming it into online ecommerce website.
 Making online ecommerce platform for buyers to buy apparels from website.
 Customers/ buyers will be able to search for the various kinds of apparels for e.g. Shirts. Jeans etc
and will be able to order it from website by making online payment of products.
 Business owner will be able to manage his products by category and prices with different sizes &
colors. Owner will be able to deliver the items to the buyers on shipping address mentioned by the
buyer while placing an order.
 Customer will be able to track their order shipment.
3.1.2 Background
Website is necessary for simplifying the buying and selling process of apparels . Customers should be able to
search the desired items and can place the order by making online  payment of the items.  Online website will
help business owner to streamline his offline business of apparels selling and will grow his revenue by making
business online.
3.1.3 Business Drivers
 Customers are looking for faster delivery of items with good quality and services.
 Customers/ buyers are going to be a main end user of the website who searches for the good quality
cloths in reasonable price.
 Admin is the Business Owner who will be responsible for managing the product catalog, categories
and prices and shipping services on website.
Page 7
3.2 Project Scope
The scope of the project is to design and develop an online ecommerce website for apparels.
Customers will be able to use the frontend website for searching the apparels and place the
order by making online payment of the order in advance. Web based admin panel/ backend will
help admin user i.e. business owner to manage the products, categories, prices and orders
placed by the customers.
3.2.1 In Scope Functionality
 Buyer
o Login
o Registration
o Search products
o Product listing and search results
o Product details with available variations
o Add to cart
o Add to wishlist
o Checkout and Online payment of the orders
o Share products on social media
o Ratings and review on products
o Place the order
o Manage address book
o My account
o Order history
o Order tracking
 Admin
o Ability to create/edit/delete products
o Manage product categories and sub-categories
o Manage product catalog
o Manage orders
o Manage customers
o Manage shipping
o Manage payments
o Manage roles/ permissions
o CMS pages management
o Ratings and reviews management
o Statistics and reports
3.2.2 Out of Scope Functionality
 Ordering customized products
 Real time order tracking
 Cash on delivery option for buyers
Page 4
3.3 User Roles
Role Description
Visitors  Visitors will be able to search for the produ

---

## 2. Technical Architecture, Workflows & Operational Methodologies

s about the product on product detail
page:
o Product title
o Thumbnail image
o Product images
o Product description
o Price
o Sizes/ colors
o Ratings & reviews
 User will be able to add the product to his shopping cart. User will also be able to add
the product to wishlist.
Buyer/ Guest
user
Page 15
Req# Priority Description Rationale Impacted
Stakeholders
 User will be able to share product on social media.
 User will not be able to add the product to wishlist without login.
FR-006 2 Wishlist
 Buyer will need to get registered and login into website to maintain his list of items in
wishlist.
 Buyer will be able to view/ add/delete products added into his wishlist. User will be
able to proceed for checkout process of items available in wishlist.
Buyer
FR-007 1 Shopping cart
 The products can be added into shopping cart from the product detail page.
 User is required to get register and login to manage the items in his shopping cart.
 User will be able to add items/remove items/ update quantity of items in shopping
cart.
 User will be able to proceed for checkout of any items/ all items available in shopping
cart.
 User will be able to view item price, sub-total and total price of the items available in
shopping cart.
Buyer
FR-008 1 Checkout &
Payment
 Payment and checkout process of the items selected from the shopping cart will be
considered for placing the orders.
 Buyer is required to login into website for checkout and payment.
 Buyer will required to enter billing and shipping address before checkout and
payment.
 Buyer will be required to select payment method for order payment
o Credit card/ debit card
o Net banking
 Buyer will be able to view the order summary on this page. Order summary will show
following details:
o Item total
o Sub-total
o Shipping cost
o Tax
Buyer
Page 15
Req# Priority Description Rationale Impacted
Stakeholders
o Order total
 Buyers will be able to receive email notifications for the orders status update.
FR-009 4 Social media
sharing
 User will be able to share product on social media.
 Login is not mandatory to share products on social media.
Buyer/ Guest
user
FR-010 1 My Account
 Buyers will be able to manage their following details from account section
o Profile details : email, phone number
o Change password
o Addresses
 Buyer will be able to access below sections from My account:
o My Orders
o MY wishlist
o shopping cart
o Ratings and reviews
o Logout
Buyer
FR-011 2 Ratings &
Reviews
 User will be able to give ratings and review to the items which he has ordered in past/
recently.
 User will be able post rating and review only for the products which he has ordered
from the website.
 Login and registration will be mandatory for the user to post ratings and review.
Buyer
FR-012 1 Order History
 Buyers will be able to view the orders list i.e. orders placed by the buyer on past.
 User will be able to view all details about the orders with total amount paid, shipping
address, items quantity, price per unit etc.
 User will be able to reorder the items which are shown in the order details.
 User will be able to track his current orders from my orders section.
Buyer
FR-013 2 Contact  Buyers will be able to contact support team via email regarding any queries/ Buyer, Admin
Page 15
Req# Priority Description Rationale Impacted
Stakeholders
Support complaints by simply posting name, email, contact number and message to the
admin.
 Admin will be able to receive an email regarding complaint details posted by buyer.
user
FR-014 1 Login
 The admin will be able to login to the admin panel.
 The admin will be asked to enter the user name and password in the given field.
 Reset password option for the admin to reset password in case of forgot password.
Admin user/
Sub-users
FR-015 1 Dashboard
 Admin user will be able to view following information on dashboard
o Total no. of active and inactive registered buyers
o Total no. of Products uploaded on website
o Total Revenue: today/ this month
Admin user/
Sub-users
FR-016 1 Buyers
Management
 Admin user will be able to view/edit/active/inactive buyers account  information from
this section.
 Admin user will be able to view all detail of the buyer’s account like profile details,
address, orders, wishlist, items in cart.
Admin user/
Sub-users
FR-017 1 Orders
Management
 Admin user will be able to view list of all orders placed by the buyers on website with
current status of each order.
 Admin user will be able to view/

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

 Admin user will be able to view/edit order details.
 Admin user will be able to update the status of order placed by the buyer.
 Status of the orders will be as below:
o Open
o Confirmed
o In process
o Shipped
o Delivered
o Admin user will be responsible for shipment of orders placed by the buyers.
 Admin user will be able to maintain the below shipment details into system for each
Admin user/
Sub-users
Page 15
Req# Priority Description Rationale Impacted
Stakeholders
order:
o Shipping carrier
o Tracking ID
o Current status of shipment
o Delivery location/address
o Shipping cost
FR-018 1
Product
categories
management
 Admin user will be able add/edit/active/inactive product categories and sub -
categories from this section.
 User will be able to add products under these categories & sub -categories from the
product management section.
Admin user/
Sub-users
FR-019 1 Products
management
 Admin user will be able to Add/ Edit/Active/ Inactive products in catalog from this
section.
 Admin user will also be able to manage following information of the products:
o Product name
o Images
o Description
o Keywords
o Variations : color, size
Admin user/
Sub-users
Payment
Management
 Ability for the admin to view/edit payment information i.e. bank account details to
receive orders payments from buyers.
 Admin user will be able to view payment status of each order placed by the buyers.
 Stripe payment gateway will be used for online payment gateway integration.
Admin user
FR-020 3 Ratings &
Review
 Admin user will be able to approve/ reject ratings and reviews posted by the buyers
for products.
Admin user/
Sub-users
FR-021 2 Statistics &
Reports
 User will be able to view the following reports in system:
o Products uploaded:
Admin user/
Sub-users
Page 15
Req# Priority Description Rationale Impacted
Stakeholders
- Date : From-To
- Month
- Year
o Revenue/ total sale
- Today
- Current week
- Date : From-To
- Month
- Year
 Admin user will be able to export reports into pdf and excel format.
FR-022 2 System users
Management
 Admin user will be able to create/edit/delete/ active/inactive sub -users to operate
the various sectional operations in system
Admin user/
Sub-users
FR-023 2 Roles
Management
 Ability to add/edit/delete/active/inactive sub-admin users with role based access Admin user/
Sub-users
FR-024 1 CMS
Management
 Admin user will be able to edit the content for below CMS pages:
o About us
o Contact us
o Privacy policy
o Terms and conditions
Admin user/
Sub-users
FR-025 3 Email
Management
 Admin user will be able to add/edit/delete content for emails to be sent to buyers
regarding new product launch, offers, and promotions.
Admin user/
Sub-users
FR-026 2 Complaints/
Feedbacks
 Admin user will be able to view queries/ complaints/ feedbacks received from the
buyers. Admin will also receive an email regarding the feedback / complaints and
queries sent by the buyers.
Admin user/
Sub-users
Page 15
5.2 Non-Functional Requirements
ID Requirement
NFR-001 Scalability: The website repository shall accommodate up to 100 users concurrently.
NFR-002 Speed: web pages should not take more than 30 seconds to load in good speed of internet.
NFR-003 Reliability: Web pages should not get broken and display page not found error if page is not available.
NFR-004 Security: SSL security and encryption for online payments
Page 16
6 Appendices
6.1 List of Acronyms
Not Applicable
6.2 Glossary of Terms
Not Applicable
6.3 Related Documents
Not Applicable

