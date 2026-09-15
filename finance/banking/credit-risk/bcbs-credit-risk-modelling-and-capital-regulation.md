---
id: finance/banking/credit-risk/bcbs-credit-risk-modelling-and-capital-regulation
canonical_question: How do banking supervisors and Basel IRB frameworks evaluate internal
  credit risk models for regulatory capital?
aliases:
- BCBS credit risk modelling
- Basel IRB internal ratings based
- regulatory capital credit risk
- stress testing credit models
- supervisory validation of credit models
entity_type: supervisory_standard
domain: finance > banking > credit-risk
last_verified: '2026-09-15'
---

# Basel Committee (BCBS) Credit Risk Modelling: Current Practices and Regulatory Capital Applications

## 1. Overview, Core Concepts & Regulatory Scope

CREDIT RISK MODELLING:
CURRENT PRACTICES
AND
APPLICATIONS
Basle Committee on Banking Supervision
Basle
April 1999
TABLE OF CONTENTS
List of Participants
Executive Summary
Part I: Introduction
1. Overview ...............................................................................................    8
2. Internal Applications of Credit Risk Models ........................................    9
3. Key Challenges to Regulatory Application............................................  10
4. Organisation of Report ...........................................................................  11
Part II: Overview of Conceptual Approaches to Credit Risk Modelling
1. Economic Capital Allocation .................................................................  13
A. Probability Density Function of Credit Losses .............................  13
B. Key Issues ......................................................................................  16
2. Measuring Credit Loss ...........................................................................  16
A. Time Horizon ................................................................................  16
B. Default-Mode Paradigm.................................................................  17
An Illustration: The Mean/Standard Deviation Approach ............  18
Internal Risk Rating Systems, EDFs, Transition Matrices ............  19
C. Mark-to-Market Paradigm .............................................................  22
Discounted Contracual Cash Flow Approach...............................  22
Risk-Neutral Valuation Approach..................................................  23
D. Key Issues ......................................................................................  24
3. Probability Density Functions................................................................  26
A. Measurement..................................................................................  26
B. Key Issues ......................................................................................  27
4. Conditional versus Unconditional Models.............................................  28
A. Definition of Approaches...............................................................  28
B. Key Issues ......................................................................................  29
5. Approaches to Credit Risk Aggregation ................................................  29
A. Top-Down and Bottom-Up Approaches........................................  29
B. Key Issues ......................................................................................  30
6. Correlations between Credit Events .......................................................  31
A. Overview........................................................................................  31
B. Cross-Correlations between Different Events................................  31
C. Correlations Among Defaults or Ratings Migrations ....................  32
Structural Models...........................................................................  32
Reduced-Form Models...................................................................  32
D. Key Issues

---

## 2. Technical Frameworks, Methodologies & Operations

ted to date reflect actuarial-based unconditional
estimates of EDFs/rating transitions and correlations that are designed to capture
29
long-run average values of these parameters.  At a given point in time, however,
such long-run averages may seriously misrepresent the short-term outlook, which
may well be highly dependent on the state of the economy. 11 Both EDFs and
correlations are likely to vary systematically with the course of the business cycle.
In contrast to actuarial-based unconditional models, a conditional model of the
type set out above incorporates in its formulation the possibility that the holding
period interval may be a period of high expected default.  Additionally,
unconditional approaches to estimating EDFs will not reflect important variables
known to affect loan performance. On the other hand, conditional techniques may
also have drawbacks; for example, a conditional model may underestimate losses
just as the credit cycle enters a downturn and overestimate losses just as the cycle
bottoms out. Further, a full reflection of business cycle effects is a complex and
difficult process, raising the possibility that parameter estimates may be subject to
considerable uncertainty.
• Ultimately, the question of whether unconditional or conditional approaches to
credit risk modelling offer a bank the best prospects for model stability and
reliability is an empirical one.
5. Approaches to Credit Risk Aggregation
A. Top-down and bottom-up approaches
Within most credit risk models, broadly the same conceptual framework is used in
modelling individual-level credit risk for different product lines; differences in
implementation arise primarily in the ways the underlying parameters are estimated using
available data (see Part III for a discussion of parameter estimation).  For most of the banks
surveyed, credit risk is measured at the individual asset level for corporate and capital market
instruments (a so-called “bottom-up” approach), while aggregate data is used for quantifying
risk in consumer, credit card or other retail portfolios (a so-called “top-down” approach ).
However, while the literature on credit risk models tends to make a distinction between these
11 See Pamela Nickell, William Perraudin and Simone Varotto, “Stability of Ratings Transitions”, September
1998. This study identifies and quantifies (using Moody’s ratings histories) various factors, such as domicile and
industry of obligor, which influence rating transitions probabilities. The study also demonstrates, using ordered
probit models, that estimates of transition matrices can be improved by conditioning on the stage of the business
cycle.
30
two approaches, the differences are less clear-cut in practice. For example, different models
may be classified as “bottom-up” given their use of borrower-specific information to “slot”
loans into buckets, even though underlying parameters may be calibrated using aggregate
data.
Models adopting a bottom-up approach attempt to measure credit risk at the level of
each loan based on an explicit evaluation of the creditworthiness of the portfolio’s constituent
debtors. Each specific position in the portfolio is associated with a particular risk rating, 12
which is typically treated as a proxy for its EDF and/or probability of rating migration. These
models could also utilise a micro approach in estimating each instrument’s LGD. The data is
then aggregated to the portfolio level taking into account diversification effects.
For retail customers, the modelling process is conceptually similar; however, due to the
sheer number of exposures, models tend to adopt a more top-down empirical approach. In this
instance, loans with similar risk profiles, such as credit scores, age and geographical location,
are aggregated into buckets, and credit risk is quantified at the level of these buckets. Loans
within each bucket are treated as statistically identical. In estimating the distribution of credit
losses, the model-builder would attempt to model both the (annual) aggregate default rate and
the LGD rate using historical time-series data for that risk segment taken as a whole, rather
than by arriving at this average through the joint consideration of default and migration risk
factors for each individual loan in the pool.
B. Key Issues
• As noted above, the distinction between top-down and bottom-up models is
typically not precise; the key consideration is the degree to which a bank can
distinguish meaningfully bet

---

## 3. Best Practices, Governance & Execution Standards

e
correlation between risk
rating movements, as well as
default.
• Most models use correlation data
generated from equity price
movements.
• Other banks rely on their judgement
to establish correlations.
• Is it reasonable to use equity
information to estimate correlations
for bank credits?
• Lack of historical data is a very
significant problem for this
parameter.
• Outside the United States, there is
even less information.
41
59
Credit Spreads Determine the appropriate
credit spreads to use to
discount future cash flows for
M-T-M purposes.
• Banks tend to use credit spreads
commonly quoted in the market for
loans that fall into public debt rating
buckets.
• How is “liquidity” element of credit
spreads taken into consideration?
45
Exposure Levels
(e.g. amount
drawn at
default)
Determine the appropriate
exposure amount to use
within the model.
• Banks attempt to determine a credit
equivalency when the exposure is
not known with certainty (e.g.
undrawn commitments).
• Banks attempt to determine future
and average exposure amounts or
estimate a credit equivalent amount
on market-driven instruments.
• Accuracy of estimates. 45
Characterisation
of Credit
Determine the appropriate
industry and country in which
to slot the credit.
• Banks using a combination of
judgement and financial statement
information based on sales and
assets.
• Accuracy of judgement-based
characterisations.
• Lack of information to fully support
industry/country assignments.
43
System Capacity Are bank systems able to
capture needed data and can
data from multiple systems be
combined?
• Significant differences in how
information is collected and what is
collected.
• Insufficient information being
collected.
• Significant system upgrades/changes
needed if information is to be
collected.
47
Management
Information
Systems
Is accurate, timely and
understandable information
being prepared for
management?
• Reporting processes tend to be in the
very early stages of development.
• Some applications take a great length
of time to run analysis.
47
60
Credit Risk Modelling - Validation Issues
Item: Description: Range of Practice: Issues/concerns: Page #
Reference:
Management
Oversight
What is the current state of
bank management’s ability to
provide reasonable oversight
to this area?
• Most knowledge/expertise of
modelling process currently lies in
backroom analytics.
• Line management and senior
management need to gain
understanding of strengths and
weaknesses.
54
Backtesting Verification that actual losses
correspond to projected
losses.
• No banks have completed any
significant backtesting.
• Limited availability of historical
data is a big hurdle.
• To date there is no way to verify
accuracy.
• Questions remain as to how to
adequately backtest.
51
Stress testing Determine the model results
under various economic
scenarios.
• Some institutions are doing work in
this area; however, to date, we have
not seen comprehensive work.
• Few institutions are doing stress
testing.
53
Sensitivity
Analysis
Assess the sensitivity of
results to changes in the
inputs (parameters)
• Very limited work completed in this
area to date.
• Sensitivity information is very
limited. Significant enhancements
needed to understand effects of
parameter changes.
53
Internal Review
and Audit of
Models
Does bank have an
independent review process to
determine the reasonableness
of the models?
• Most banks do not have an internal
review process in place.
• Lack of independence in reviewing
these processes.
54

