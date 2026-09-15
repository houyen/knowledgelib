---
id: health/healthcare-domain/healthcare-domain-payer-provider-claims-handbook
canonical_question: What is the end-to-end structure of the US healthcare industry,
  including payers, providers, claims adjudication, and HIPAA EDI standards?
aliases:
- healthcare domain course material
- payer provider relationship healthcare
- claims lifecycle adjudication EDI 837 835
- HMO PPO POS benefit plan design
- HIPAA compliance and ICD CPT coding
entity_type: domain_master_handbook
domain: health > healthcare-domain
last_verified: '2026-09-15'
---

# Healthcare Domain Master Handbook: Payers, Providers, Benefit Plans, Claims & HIPAA

## 1. Overview, Core Concepts & Scope

Table of Contents

 TOC \o "1-3" \h \z  HYPERLINK \l "_Toc331861" 1	Healthcare Market Overview	 PAGEREF _Toc331861 \h 5
 HYPERLINK \l "_Toc331862" 1.1	Introduction	 PAGEREF _Toc331862 \h 5
 HYPERLINK \l "_Toc331863" 1.2	What is an HMO?	 PAGEREF _Toc331863 \h 5
 HYPERLINK \l "_Toc331864" 1.3	The Industry Outlook	 PAGEREF _Toc331864 \h 6
 HYPERLINK \l "_Toc331865" 1.3.1	Trends in Healthcare – Provider Space	 PAGEREF _Toc331865 \h 6
 HYPERLINK \l "_Toc331866" 1.3.2	Trends in Healthcare – Payer Space	 PAGEREF _Toc331866 \h 7
 HYPERLINK \l "_Toc331867" 1.4	Key Players	 PAGEREF _Toc331867 \h 8
 HYPERLINK \l "_Toc331868" 1.5	References	 PAGEREF _Toc331868 \h 8
 HYPERLINK \l "_Toc331869" 2	Healthcare Overview	 PAGEREF _Toc331869 \h 9
 HYPERLINK \l "_Toc331870" 2.1	Unit Objectives	 PAGEREF _Toc331870 \h 9
 HYPERLINK \l "_Toc331871" 2.2	Genesis Of Healthcare	 PAGEREF _Toc331871 \h 9
 HYPERLINK \l "_Toc331872" 2.3	How the industry Works?	 PAGEREF _Toc331872 \h 10
 HYPERLINK \l "_Toc331873" 2.4	Healthcare pillars.	 PAGEREF _Toc331873 \h 12
 HYPERLINK \l "_Toc331874" 2.4.1	Members.	 PAGEREF _Toc331874 \h 12
 HYPERLINK \l "_Toc331875" 2.4.2	Providers.	 PAGEREF _Toc331875 \h 12
 HYPERLINK \l "_Toc331876" 2.4.3	Benefits.	 PAGEREF _Toc331876 \h 13
 HYPERLINK \l "_Toc331877" 2.4.4	Claims.	 PAGEREF _Toc331877 \h 14
 HYPERLINK \l "_Toc331878" 2.4.5	Sales.	 PAGEREF _Toc331878 \h 15
 HYPERLINK \l "_Toc331879" 2.4.6	External Agents.	 PAGEREF _Toc331879 \h 16
 HYPERLINK \l "_Toc331880" 2.5	Healthcare workflow.	 PAGEREF _Toc331880 \h 17
 HYPERLINK \l "_Toc331881" 2.6	Summary.	 PAGEREF _Toc331881 \h 18
 HYPERLINK \l "_Toc331882" 2.7	Review Questions.	 PAGEREF _Toc331882 \h 19
 HYPERLINK \l "_Toc331883" 2.8	References.	 PAGEREF _Toc331883 \h 19
 HYPERLINK \l "_Toc331884" 3	Members	 PAGEREF _Toc331884 \h 22
 HYPERLINK \l "_Toc331885" 3.1	Unit Objective	 PAGEREF _Toc331885 \h 22
 HYPERLINK \l "_Toc331886" 3.2	Introduction	 PAGEREF _Toc331886 \h 22
 HYPERLINK \l "_Toc331887" 3.2.1	Insurance Business: An Overview.	 PAGEREF _Toc331887 \h 23
 HYPERLINK \l "_Toc331888" 3.3	Individual and Group Insurance in detail	 PAGEREF _Toc331888 \h 24
 HYPERLINK \l "_Toc331889" 3.3.1	Individual Insurance	 PAGEREF _Toc331889 \h 24
 HYPERLINK \l "_Toc331890" 3.3.2	How to get individual insurance?	 PAGEREF _Toc331890 \h 24
 HYPERLINK \l "_Toc331891" 3.3.3	Group Insurance	 PAGEREF _Toc331891 \h 26
 HYPERLINK \l "_Toc331892" 3.3.4	Company Paid Groups	 PAGEREF _Toc331892 \h 28
 HYPERLINK \l "_Toc331893" 3.3.5	Affinity Groups	 PAGEREF _Toc331893 \h 29
 HYPERLINK \l "_Toc331894" 3.3.6	Self Insured Group	 PAGEREF _Toc331894 \h 29
 HYPERLINK \l "_Toc331895" 3.3.7	Self-Employed Members	 PAGEREF _Toc331895 \h 29
 HYPERLINK \l "_Toc331896" 3.3.8	Exercise	 PAGEREF _Toc331896 \h 31
 HYPERLINK \l "_Toc331897" 3.4	Member’s enrollment	 PAGEREF _Toc331897 \h 32
 HYPERLINK \l "_Toc331898" 3.4.1	What is Enrollment?	 PAGEREF _Toc331898 \h 32
 HYPERLINK \l "_Toc331899" 3.4.2	How is enrollment carried out?	 PAGEREF _Toc331899 \h 32
 HYPERLINK \l "_Toc331900" 3.4.3	Output of enrollment process	 PAGEREF _Toc331900 \h 33
 HYPERLINK \l "_Toc331901" 3.4.4	Enrollment: Overall Picture	 PAGEREF _Toc331901 \h 34
 HYPERLI

---

## 2. Technical Architecture, Workflows & Operational Methodologies

p reduce the cost of medical care. In return, the sponsor(s) attempts to increase patient volume by creating an incentive for employees or policyholders to use the physicians and facilities within the PPO network. 

PPO members usually pay for services as they are rendered. The PPO sponsor (employer or insurance company) generally reimburses the member for the cost of the treatment minus any co-payment. In some cases, the provider may submit the bill directly to the insurance company for payment. The insurer then pays the covered amount directly to the healthcare provider, and the member pays his or her co-payment amount. The healthcare providers and the PPO sponsor(s) negotiate the price for each type of service in advance. 

When a member receives care from a participating provider they receive benefits, which are at the higher level of benefit coverage, usually 100% payment rate, known as ‘Preferred Benefits’.

When members receive care from a non-participating provider they receive benefits, which are at the lower level of benefit coverage, usually 80% payment rate, known as ‘Non-Preferred Benefits’.

Advantages 

Free choice of healthcare provider, as PPO members are not required to seek care from PPO physicians. However, there is a strong financial incentive to do so. For example, members may receive 90% reimbursement for care obtained from in-network physicians but only 60% for out-of-network treatment. In order to avoid paying an additional 30% out of their own pockets, most PPO members choose to receive their healthcare within the PPO network.

Disadvantages

As mentioned previously, there is a strong financial incentive to use PPO network physicians. For example, members may receive 90% reimbursement for care obtained from in-network providers but only 60% for treatment provided by out-of-network providers. Thus, if a member’s longtime family doctor is outside of the PPO network, he may choose to continue seeing him, but it will cost more. 

A PPO member has to file claims on his own. Additionally, most PPOs have larger co-payment amounts than HMOs, and members may be required to meet a deductible. Hence, the expenses and paperwork are higher as compared to HMOs.

A typical PPO plan will look like this –

PRIVATEPlan Feature
Preferred Benefit
Non-preferred Benefit
Calendar Year Deductible
None
$200.00
Per Confinement deductible
None
$200.00
Family Limit Deductible
None
3x deductible
Copay
$10.00 office visit
None
Coinsurance
100%
80% / 20%
Coinsurance Limit
None
$1000.00
Physicians
100% after $10.00 copay
80%/20%
Emergency room
$25.00
Same as preferred if true emergency, else none. 
Hospital
100%
80% / 20%
Other Covered Services
100%
80% / 20%
Table  SEQ Table \* ARABIC 3: A sample PPO plan

Preferred option closely mirrors the HMO option while the non-preferred option approaches the Indemnity option.

The benefits are reduced in case of non-preferred option. 

Point Of Service  (POS)
POS plans give two benefit levels. The plan can be visualized as having 2 sides. One side is for in-network services and the other side is for out-of-network services. 

When a member uses the in-network benefits, the POS plan mirrors an HMO. Like an HMO, the member pays no deductible and usually only a minimal co-payment when he uses an in-network healthcare provider. But, he also must choose a primary care physician who is responsible for all referrals within the POS network.

When he uses the out-of-network benefits, the POS plan is an indemnity plan. The member will likely be subject to a deductible and co-payment.
 
Advantages

POS coverage allows a member to increase his freedom of choice. Like a PPO, he can mix the types of care he receives. For example, the member’s child could continue to see his pediatrician who is not in the network, while the member himself receives his healthcare from in-network providers. POS plan encourages members to use in-network providers but does not make it mandatory, as with HMO coverage.

As with HMO coverage, members pay only a nominal amount for in-network care. Usually, co-payment is around $10 per treatment or office visit. Unlike HMO coverage, members always retain the right to seek care outside the network at a lower level of coverage.

No deductible is required for in-network services, while there is no PCP for out-of-network services.

Disadvantages

There are substantial co-payments and deductibles for out-of-network care.
In most cases, members must have paid a specified deduct

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

er to visit a specialist doctor for further treatment.

Benefit Code : Code assigned to Benefits, benefits meaning Medical Services (Service Types - say Surgery) Insurance company will pay for, fully or partially.

Rider :  These are add-ons to basic plan at some extra cost and will cover additional benefits. Generally observed for Indemnity Plans.

Capitation :  Fixed amount of money paid to provider, on monthly basis and/or per member basis ,for full medical care of an individual.

Primary care Physician :  The physicians/doctors providing full range of basic health services to patients. The member is expected to consult its PCP first for any kind of health service for HMO care . 

Drug Code : Code for medication provided as a part of treatment.

Proc/Service Code : Code for particular service coming under particular service type. The service is specific whereas service type is generic.

Self Insured Groups : Some companies like (Eg. AT&T) makes contrat with healthcare companies for adjudicating claims for a fixed sum of money, where in the company (i.e. AT&T ) provides insurance for its employees by collecting money from them annually ( funding or contribution) . 
					Healthcare Market Overview
___________________________________________________________________

PAGE  

__________________________________________________________________________________
 FILENAME Healthcare Domain Course Material	Ver. 1.0	Page  PAGE 1 of  NUMPAGES 145

						Healthcare Overview
___________________________________________________________________

							Members
___________________________________________________________________

__________________________________________________________________________________
 FILENAME Healthcare Domain Course Material	Ver. 1.0	Page  PAGE 24 of  NUMPAGES 146

							Members
___________________________________________________________________

							Providers
___________________________________________________________________

								Sales
___________________________________________________________________

 FILENAME Healthcare Domain Course Material	Ver 0.00a	Page  PAGE 61 of 150

							Benefits
___________________________________________________________________

								Claims
___________________________________________________________________

						External Agents
___________________________________________________________________

							Summary
___________________________________________________________________

							Appendix
___________________________________________________________________

							Glossary
___________________________________________________________________

PAGE \# "'Page: '#' '"  
Name of Insurance Firm selling the planPAGE \# "'Page: '#' '"  
PAGE \# "'Page: '#' '"  
PAGE \# "'Page: '#' '"  Name of Plan
PAGE \# "'Page: '#' '"  Contact persons at Selling Company

Member's data

Asks for Service

Files Claims

Files Claims

Check Eligibility

Insurer

Claim's Adjudication

Providers

Member's Enrollment

Payment

Payment

Member

Member

Member

Insurance Company

Associations

Employer

Insurer

Member's Policy information

Member's Policy information

Member's Policy information

Provider

Member

Employer		

Marketing assistants

Fig 2

EDI Claim

PROVIDER

MEMBER

Receipts

Encounter

CLAIMS
SYSTEM

Check to 
Provider/ Member

Check Information

REFERRAL
SYSTEM

Referral

Verification

Paper Claim

ENVOY

IKFI

EDI

Pre-receipts

ACCOUNTS
PAYABLE

DENIALS

 EMBED PowerPoint.Slide.8

