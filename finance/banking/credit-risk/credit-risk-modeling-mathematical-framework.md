---
id: finance/banking/credit-risk/credit-risk-modeling-mathematical-framework
canonical_question: What are the mathematical models (Merton, CreditRisk+, copulas)
  used to measure and manage portfolio credit risk?
aliases:
- credit risk modeling framework
- structural Merton default model
- CreditRisk+ portfolio loss distribution
- probability of default PD loss given default LGD
- credit VaR and expected shortfall
entity_type: quantitative_risk_manual
domain: finance > banking > credit-risk
last_verified: '2026-09-15'
---

# Quantitative Credit Risk Modeling: Default Probabilities, Merton Model, and Portfolio Loss Distributions

## 1. Overview, Core Concepts & Regulatory Scope

©2003 CRC Press LLC
Preface
In banking, especially in risk management, portfolio management, and
structured ﬁnance, solid quantitative know-how becomes more and
more important. We had a two-fold intention when writing this book:
First, this book is designed to help mathematicians and physicists
leaving the academic world and starting a profession as risk or portfolio
managers to get quick access to the world of credit risk management.
Second, our book is aimed at being helpful to risk managers looking
for a more quantitative approach to credit risk.
Following this intention on one side, our book is written in a Lecture
Notes style very much reﬂecting the keyword “introduction” already
used in the title of the book. We consequently avoid elaborating on
technical details not really necessary for understanding the underlying
idea. On the other side we kept the presentation mathematically pre-
cise and included some proofs as well as many references for readers
interested in diving deeper into the mathematical theory of credit risk
management.
The main focus of the text is on portfolio rather than single obligor
risk. Consequently correlations and factors play a major role. More-
over, most of the theory in many aspects is based on probability theory.
We therefore recommend that the reader consult some standard text
on this topic before going through the material presented in this book.
Nevertheless we tried to keep it as self-contained as possible.
Summarizing our motivation for writing an introductory text on
credit risk management one could say that we tried to write the book we
would have liked to read before starting a profession in risk management
some years ago.
Munich and Frankfurt, August 2002
Christian Bluhm, Ludger Overbeck, Christoph Wagner
©2003 CRC Press LLC
Acknowledgements
Christian Bluhm would like to thank his wife Tabea and his children
Sarah and Noa for their patience during the writing of the manuscript.
Without the support of his great family this project would not had
come to an end. Ludger Overbeck is grateful to his wife Bettina and
his children Leonard, Daniel and Clara for their ongoing support.
We very much appreciated feedback, support, and comments on the
manuscript by our colleagues.
Questions and remarks of the audiences of several conferences, sem-
inars and lectures, where parts of the material contained in this book
have been presented, in many ways improved the manuscript. We al-
ways enjoyed the good discussions on credit risk modeling issues with
colleagues from other ﬁnancial institutions. To the many people dis-
cussing and sharing with us their insights, views, and opinions, we are
most grateful.
Disclaimer
This book reﬂects the personal view of the authors and not the opin-
ion of HypoVereinsbank, Deutsche Bank, or Allianz. The contents of
the book has been written for educational purposes and is neither an of-
fering for business nor an instruction for implementing a bank-internal
credit risk model. The authors are not liable for any damage arising
from any application of the theory presented in this book.
©2003 CRC Press LLC
About the Authors
Christian Bluhm works for HypoVereinsbank's group portfolio m

---

## 2. Technical Frameworks, Methodologies & Operations

e call and put options.
Therefore, increased volatility (higher risk) is
• good for equity holders, because their natural risk position is
a long call, and the value of the call increases with increasing
volatility;
• bad for debt holders, because their natural risk position 4 is a
short put, whose value decreases with increasing volatility.
Note the unsymmetry in the position of equity holders: Their downside
risk is limited, because they can not lose more than their invested
capital. In contrast, their upside potential is unlimited. The better the
ﬁrm performs, the higher the value of the ﬁrm’s assets, the higher the
remaining of assets after a repayment of debt in case the equity holders
liquidate the ﬁrm.
3.3.2 Asset from Equity Values
The general problem with asset value models is that asset value pro-
cesses are not observable . Instead, what people see every day in the
stock markets are equity values. So the big question is how asset values
can be derived from market data like equity processes. Admittedly, this
is a very diﬃcult question. We therefore approach the problem from
two sides. In this section we introduce the classical concept of Merton,
saying how one could solve the problem in principle . In the next sec-
tion we then show a way how the problem can be tackled in practice .
4Which could only be neutralized by a long put.
©2003 CRC Press LLC
We follow the lines of a paper by Nickell, Perraudin, and Varotto [101].
Infact,therear ecertainlymoreworkingapproachesfortheconstruc-
tionofassetvaluesfrommarketdata.Forexample ,intheirpublished
papers (see, e.g., Crosbie [19]) KMV incorporates the classical Merton
model,buti tiswellknownthatintheircommercialsoftware(seeSec-
tion1.2.3)theyhaveimplementedadiﬀerent,mor ecomplicated,and
undisclosed algorithm for translating equity into asset values.
The classical approach is as follows: The process of a ﬁrm’s equity
is observable in the market and is given by the company’s market cap-
italization, deﬁned by
[number of shares] × [value of one share] .
Also observable from market data is the volatility σE of the ﬁrm’s equity
process. Additional information we can get is the book value of the
ﬁrm’s liabilities. From these three sources,
• equity value of the ﬁrm,
• volatility of the ﬁrm’s equity process, and
• book value of the ﬁrm’s liabilities,
we now want to infer the asset value process (At)t≥0 (as of today).
Once more we want to remark that the following is more a “schoolbook
model” than a working approach. In contrast, the next paragraph will
show a more applicable solution.
Let us assume we consider a ﬁrm with the same simple capital struc-
ture5 as introduced in (3. 5). From Conclusion 3.3.2 we already know
that the ﬁrm’s equity can be seen as a call option on the ﬁrm’s assets,
written by the ﬁrm to the equity or share holders of the ﬁrm. The
strike price F is determined by the book value of the ﬁrm’s liabilities,
and the maturity T is set to the considered planning horizon, e.g., one
year. According to (3. 7) this option-theoretic intepretation of equity
yields the functional relation
E
t = Ct(At,σA,F, (T − t),r) ( t∈ [0,T]) (3. 8)
5Actually it is in part due to the assumption of a simple capital structure that the classical
Merton model is not really applicable in practice.
©2003 CRC Press LLC
Thisfunctionalrelationcanbelocallyinverted ,duetothe implicit
functiontheorem ,inorde rtosol ve(3.8)for At.Therefore,th easset
valueoftheﬁr mcanbecalculatedasafunctionoftheﬁrm’ sequity
andtheparameters F,t,T,r, andth eassetvolatility σA.If ,aswe
alreadyremarked ,assetvalu eprocesse sarenotobservable ,theasset
volatilityals oisnotobservable .Itthereforeremain stodetermin ethe
assetvolatility σA inordertoobtain At from(3.8).
Here,weactuallyneedsomeinsightsfromstochasticcalculus ,su ch
thatforabriefmomentwearenowforce dtouseresultsforwhichan
exactan dcompleteexplanationisbeyondthescopeofthebook.How-
ever,inthenex tsectionwewillprovidesom e“heuristic”background
on pathwisest ochasticintegrals ,suchthatatleastsomeopenquestions
willbeansweredlate ron.Asalwaysweassumeforth esequelthat
allrandomvariablesrespectivelypr ocessesaredeﬁne donasuitable
commonprobabilityspace.
Recallthatweassumedthattheasse tvalueproces s( At)t≥0 isas-
sumedtoe volvelikea geometricBrownianmotion (seeSection3.2.1),
meaning that A solves the stochastic diﬀerential equation
At − A0 = µA
t∫
0
As ds+ σA
t∫
0
As dB(A)
s .
Following almost literally the arguments in Merton’s approach, we as-
sume for the e

---

## 3. Best Practices, Governance & Execution Standards

vice. Collateralized Debt Obligations Per-
formance Overview Compilation, March 2002.
[97] D. Murphy. Keeping credit under control. Risk, 9, September
1996.
[98] S.R. Neal. Credit derivatives: New ﬁnancial instruments for con-
trolling credit risk. Economic Review, 1996.
[99] R. Nelsen. An Introduction to Copulas. Springer, New York,
1999.
[100] C. Nelson and A. Siegel. Parsimonious modeling of yield curves.
Journal of Business, 60:473–489, 1987.
[101] P. Nickell, W. Perraudin, and S. Varotto. Ratings- versus equity-
based credit risk modeling: an empirical analysis. http://www.
bankofengland.co.uk/workingpapers/, 1999. Working paper.
[102] J. Norris. Markov Chains . Cambridge Series in Statistical and
Probabilistic Mathematics. Cambridge University Press, 1998.
[103] Basel Committee on Banking Supervision. The Internal Ratings-
Based Approach. Supporting Document to the New Basel Capital
Accord, 2001.
[104] M. K. Ong. Internal Credit Risk Models . Risk Books, 1999.
©2003 CRC Press LLC
[105] L. Overbeck. Allocation of economic capital in loan portfolios.
In U. Franke, W. H¨ardle, and G. Stahl, editors, Measuring Risk
in Complex Stochastic Systems. Springer, New York, 2000.
[106] W. R. Pestman. Mathematical Statistics. de Gruyter, 1998.
[107] PriceWaterhouseCoopers. The PriceWaterhouseCoopers Credit
Derivatives Primer, 1999.
[108] D. Revuz and M. Yor. Continuous Martingales and Brownian
Motion. Springer-Verlag, 1991. Chapter IV (3.13).
[109] J. A. Rice. Mathematical Statistics and Data Analysis. Duxbury
Press, 2nd edition, 1995.
[110] W. Schmidt and I. Ward. Pricing default baskets. Risk,
15(1):111–114, January 2002.
[111] Ph. J. Schoenbucher. Factor models for portfolio credit risk.
Preprint, University of Bonn, Germany, 2001.
[112] J. Skarabot. Asset securitization and optimal asset structure of
the ﬁrm. Working Paper, July 2001.
[113] A. Sklar. Fonction de repartition `an dimension et leur marges.
Publications de l’Insitute Statistique de l’Universit´e de Paris,
8:229–231, 1959.
[114] A. Sklar. Random variables, joint distribution functions and cop-
ulas. Kybernetika, 9:449–460, 1973.
[115] J. R. Sobehart and S. C. Keenan. An introduction to market-
based credit analysis. Moody’s Risk Management Services,
November 1999.
[116] Standard& Poor’s. Global CBO/CLO Criteria.
[117] Standard& Poor’s. Global Synthetic Securities Criteria.
[118] Standard & Poor’s. Standard& Poor’s Corporate Ratings Crite-
ria 1998.
[119] W. Stromquist. Roots of transition matrices. Daniel H. Wagner
Associates, 1996. Practical Paper.
[120] D. Tasche. Risk contributions and performance measurement.
http://www.ma.tum.de/stat/, 1999.
©2003 CRC Press LLC
[121] D. Tasche. Calculating value-at-risk contributions in Cred-
itRisk+. http://arxiv.org/abs/cond-mat/0112045, 2000.
[122] D. Tasche. Conditional expectation as quantile derivative. http:
//www.ma.tum.de/stat/, 2000.
[123] O. A. Vasicek. Probability of loss on loan portfolio. KMV Cor-
poration, 1987.
[124] O.A. Vasicek. An equilibrium characterization of the term struc-
ture. Journal of Financial Economics , 5:177–188, 1977.
[125] S. S. Wang. Aggregation of correlated risk portfolios: Models &
algorithms.
[126] T. Wilde. IRB approach explained. RISK, 14(5), 2001.
[127] T. Wilson. Portfolio credit risk, part i. RISK, pages 111–117,
1997.
[128] T. Wilson. Portfolio credit risk, part ii. RISK, pages 56–61, 1997.
[129] D. Zwillinger. Handbook of Diﬀerential Equations . Academic
Press, Boston, 1995.
©2003 CRC Press LLC

