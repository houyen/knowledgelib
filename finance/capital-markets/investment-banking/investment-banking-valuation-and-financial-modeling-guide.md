---
id: finance/capital-markets/investment-banking/investment-banking-valuation-and-financial-modeling-guide
canonical_question: How are DCF, Comparable Companies, Precedent Transactions, LBO,
  and M&A modeling executed in investment banking?
aliases:
- investment banking valuation guide
- DCF modeling mechanics
- LBO model analysis
- M&A accretion dilution
- enterprise value vs equity value
entity_type: financial_modeling_guide
domain: finance > capital-markets > investment-banking
last_verified: '2026-09-15'
---

# Investment Banking Core Technical Guide: Valuation, DCF, M&A, LBO, and Accounting

## 1. Overview, Scope & Market Context

The 400
Investment Banking Interview
Questions & Answers
You Need to Know
A
Production
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
2
Copyright 2008 – 2011 Capital Capable Media LLC.  All Rights Reserved.
Notice of Rights
No part of this book may be reproduced or transmitted in any form or by any
means, electronic, mechanical, photocopying, recording, or otherwise, without
the prior written permission of the publisher.
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
3
Table of Contents – Technical Questions
Introduction ...................................................................................................3
Technical Questions & Answers .................................................................5
Accounting Questions & Answers – Basic ............................................6
Accounting Questions & Answers – Advanced ................................ 19
Enterprise / Equity Value Questions & Answers – Basic ................. 25
Enterprise / Equity Value Questions & Answers – Advanced ........ 30
Valuation Questions & Answers – Basic ............................................. 32
Valuation Questions & Answers – Advanced ................................... 43
Discounted Cash Flow Questions & Answers – Basic ...................... 49
Discounted Cash Flow Questions & Answers – Advanced ............. 58
Merger Model Questions & Answers – Basic ..................................... 61
Merger Model Questions & Answers – Advanced ........................... 69
LBO Model Questions & Answers – Basic .......................................... 78
LBO Model Questions & Answers – Advanced ................................ 85
Brain Teaser Questions & Answers ..................................................... 92
Introduction
This guide has one purpose: to help you answer the most important “fit” and technical
questions in investment banking interviews. We tell you what’s important and what you
need to say – nothing more and nothing less.
Most other guides suffer from several problems:
1. The information is not investment banking-specific.  Do you think you’re going
to get a question about “Why you’re interested in this position?”  I’ll tell you
why you’re interested – because you want to make a lot of money!
2. The information is out-of-date, wrong or incomplete (see: The Vault Guide).
These days, interviewers assume you know the basics – like how to value a
company – and go beyond that with advanced questions that require thinking
more than memorization.
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
4
3. No answers are provided, or there’s minimal direction (see: The Recruiting Guide
to Investment Banking).  Of course, you shouldn’t memorize answers word-for-
word, but it’s helpful to have an idea of how you might structure your answers.
4. The questions do not apply to interviewees from div

---

## 2. Core Operational, Legal & Financial Mechanisms

er the Multiples Method or the Gordon Growth Method, and
then also discount that back to its Net Present Value using WACC.
Finally, you add the two together to determine the company’s Enterprise Value.”
2. Walk me through how you get from Revenue to Free Cash Flow in the projections.
Subtract COGS and Operating Expenses to get to Operating Income (EBIT).  Then,
multiply by (1 – Tax Rate), add back Depreciation and other non-cash charges, and
subtract Capital Expenditures and the change in Working Capital.
Note: This gets you to Unlevered Free Cash Flow since you went off EBIT rather than
EBT. You should confirm that this is what the interviewer is asking for.
3. What’s an alternate way to calculate Free Cash Flow aside from taking Net Income,
adding back Depreciation, and subtracting Changes in Operating Assets / Liabilities
and CapEx?
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
50
Take Cash Flow From Operations and subtract CapEx and mandatory debt repayments
– that gets you to Levered Cash Flow. To get to Unlevered Cash Flow, you then need to
add back the tax-adjusted Interest Expense and subtract the tax-adjusted Interest Income.
4. Why do you use 5 or 10 years for DCF projections?
That’s usually about as far as you can reasonably predict into the future.  Less than 5
years would be too short to be useful, and over 10 years is too difficult to predict for
most companies.
5. What do you usually use for the discount rate?
Normally you use WACC (Weighted Average Cost of Capital), though you might also
use Cost of Equity depending on how you’ve set up the DCF.
6. How do you calculate WACC?
The formula is: Cost of Equity * (% Equity) + Cost of Debt * (% Debt) * (1 – Tax Rate) +
Cost of Preferred * (% Preferred).
In all cases, the percentages refer to how much of the company’s capital structure is
taken up by each component.
For Cost of Equity, you can use the Capital Asset Pricing Model (CAPM – see the next
question) and for the others you usually look at comparable companies/debt issuances
and the interest rates and yields issued by similar companies to get estimates.
7. How do you calculate the Cost of Equity?
Cost of Equity = Risk-Free Rate + Beta * Equity Risk Premium
The risk-free rate represents how much a 10-year or 20-year US Treasury should yield;
Beta is calculated based on the “riskiness” of Comparable Companies and the Equity
Risk Premium is the % by which stocks are expected to out-perform “risk-less” assets.
Normally you pull the Equity Risk Premium from a publication called Ibbotson’s.
Note: This formula does not tell the whole story.  Depending on the bank and how
precise you want to be, you could also add in a “size premium” and “industry
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
51
premium” to account for how much a company is expected to out-perform its peers is
according to its market cap or industry.
Small company stocks are expected to out-perform large company stocks and certain
industries are expected to out-perform others, and these premiums reflect these
expectations.
8. How do you get to Beta in the Cost of Equity calculation?
You look up the Beta for each Comparable Company (usually on Bloomberg), un-lever
each one, take the median of the set and then lever it based on your company’s capital
structure.  Then you use this Levered Beta in the Cost of Equity calculation.
For your reference, the formulas for un-levering and re-levering Beta are below:
Un-Levered Beta = Levered Beta / (1 + ((1 - Tax Rate) x (Total Debt/Equity)))
Levered Beta = Un-Levered Beta x (1 + ((1 - Tax Rate) x (Total Debt/Equity)))
9. Why do you have to un-lever and re-lever Beta?
Again, keep in mind our “apples-to-apples” theme.  When you look up the Betas on
Bloomberg (or from whatever source you’re using) they will be levered to reflect the
debt already assumed by each company.
But each company’s capital structure is different and we want to look at how “risky” a
company is regardless of what % debt or equity it has.
To get that, we need to un-lever Beta each time.
But at the end of the calculation, we need to re-lever it because we want the Beta used in
the Cost of Equity calculation to reflect the true risk of our company, taking into
account its capital structure this time.
10. Would you expect a manufacturing company or a technology company to have a
higher Beta?
A technology company, because technology is viewed as a “riskier” industry than
manufacturing.
ht

---

## 3. Standards, Methodologies & Risk Guidelines

so the
hour hand will have moved ¾ of 30 degrees, or 22.5 degrees.  If we add them together,
we see that 120 + 22.5 = 142.5
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
93
The most common mistake is to state the original number we arrived at – 120 degrees –
rather than finishing the calculation.  Sometimes with this type of question the
interviewer will lead you in the right direction if you have a basic idea of how to solve it.
3. You have stacks of quarters, dimes, nickels and pennies (these represent $0.25, $0.10,
$0.05 and $0.01, respectively, in the US monetary system for anyone international).
There are an unlimited number of coins in each stack.
You can take coins from a stack in any amount and in any order and place them in
your hand.  What is the greatest dollar value in coins you can have in your hands
without being able to make change for a dollar?
$1.19.  There are a few ways to think about this, but the easiest is to start with the largest
coin – quarters – first and then work your way down.
4 quarters equals $1.00, so we clearly can’t do that – but 3 quarters are ok because that’s
only $0.75.
Next, we have dimes.  Recall that we can use any combination of coins to make change
for a dollar – if we were to have 5 dimes and put them together with the 2 quarters, that
would make $1.00.  So we’ll use 4 instead – there’s no combination there that would
result in $1.00 when added to the quarters.
Nickels are next.  Here, we can’t have any – because even a single nickel, $0.05, would
add up to $1.00 when added to the 3 quarters we have ($0.75) and the 2 dimes ($0.20).
Finally, for pennies we know that we can’t have 5 pennies ($0.05) because we could then
get to $1.00 using the same logic as we saw for the nickels.  So 4 is the maximum here.
With that, we see that 3 Quarters + 4 Dimes + 4 Pennies = $1.19
The most common mistake is not realizing you can use any combination of your existing
coins to add up to a dollar – most people understand that you can’t have 4 quarters, but
sometimes interviewees forget that 2 quarters + 5 dimes = $1.00 as well.
This is another case where asking clarifying questions – such as whether 2 quarters + 5
dimes would count as $1.00 – really helps.
http://breakingintowallstreet.com
http://www.mergersandinquisitions.com
94
4. You have a hose along with a 3 liter bucket and a 5 liter bucket.  How do you get
exactly 4 liters of water?
First, fill the 3 liter bucket and pour it into the 5 liter one.  Then, re-fill the 3 liter bucket
and pour it into the 5 liter bucket until it’s full – that leaves 1 liter in the 3 liter bucket
and 5 in the 5 liter bucket.
Then, pour out the 5 liter bucket so nothing is left and pour the 1 liter of water from the
3 liter bucket into the 5 liter bucket.  Finally, fill the 3 liter bucket completely and pour it
into the 5 liter bucket – since it already has 1 liter of water, you’ll get exactly 4 liters.
For this type of question, it’s easiest to use deductive reasoning to get the answer.  You
know you can’t possibly get 4 liters of water in the 3 liter bucket – it has to be in the 5
liter bucket.
Since you can easily get 3 liters of water, that tells you that the “trick” will involve
isolating the remaining 1 liter and getting it into the 5 liter bucket.  So then the question
comes down to how to get the 1 liter of water in the 3 liter bucket.  You know it has to
involve pouring water into the 5 liter bucket, and that leads you in the right direction.

