---
id: computing/telecom/guide-to-modern-telecom-oss-bss-architecture
canonical_question: What is modern telecom Operations Support Systems (OSS) architecture,
  including TM Forum eTOM, network automation, and service assurance?
aliases:
- guide to modern telecom OSS
- OSS BSS architecture telecom
- TM Forum Frameworx eTOM
- service fulfillment and service assurance
- 5G network slicing orchestration
entity_type: industry_architecture_guide
domain: computing > telecom
last_verified: '2026-09-15'
---

# Guide to Modern Telecom OSS/BSS Architecture: eTOM, Service Assurance & 5G Orchestration

## 1. Overview, Core Concepts & Scope

The 2019 Guide to
Modern
OSS
Copyright 2018, J E Pullen Ltd.
Produced by
With the Support of
Table of
Contents
Be the first to get updates to this guide.
Register your email address at
ossline.com
1 What is OSS and why is it
needed?
2 OSS use cases
3 OSS applications and
functions
4 Network trends and the
future of OSS
1
Welcome
Getting involved in your first OSS
project?
Start here.
This introduction to OSS assumes you
know very little about either
telecommunications operational
processes or the software and systems
used to run the network.
Starting with the basics, it will explain
why OSS plays an important role in
ensuring users of communication
services enjoy a good experience while
the operators of the networks run an
efficient, profitable business.
2
Any questions?
Ask the author
If you have any questions after reading this guide go
ahead and contact me via email ( james@ossline.c om)
or Twitter ( @ossline).
Just ask.
I’ll respond to as many questions as I can, and if I don’t
know the answer, I probably know someone who does.
Follow OSS Line
To get regular weekly updates on OSS topics and news,
sign-up at ossline.com and follow @ossline
3
Chapter One
What is OSS
and why is it needed?
Operational Support Systems (OSS) is
IT for running communications
networks.
OSS includes software, hardware, integration between
systems, and business processes. As a collection of
integrated applications, OSS supports the design, build,
monitoring and assurance of both the communications
network as a whole and the individual customer services
that make use of that network.
OSS encompasses many highly technical network
management processes but ultimately its purpose is to
ensure the network is efficient, services are profitable,
and customers are happy.
A lot of concepts have been introduced there already, so
let’s start by looking at the acronym OSS: What does OSS
stand for?
4
What does OSS
stand for?
OSS stands for either “Operational
Support Systems” or “Operations
Support Systems”.
“Operational Support Systems” is perhaps more
commonly used. But don't worry, you won't sound dumb
if you use either operations or operational.
Let's break it down further...
Operational/Operations
Relating to the day-to-day tasks of supplying and
supporting communication services. Getting technical and
infrastructure jobs done. Running the network and
services. As opposed to the business of selling, marketing
or billing (which, as we will see later, are tasks that belong
to Business Support Systems, BSS).
Support
Enabling and improving the service provider's operational
activities: Automating operational tasks; executing them
faster; making them consistent; and tracking
progress/results.
Systems
One or more distinct software applications, that are
responsible for doing specific OSS jobs, running on
servers, or on devices installed in the network, or
executed in the Cloud.
5
The role of OSS
OSS includes many applications that a service provider
requires in order to perform 'back-office' activities. The
service provider’s ‘OSS environment’ will include many
(from tens to hundreds) of separate OSS applications, each
responsible for their own part of the businesses’
operation.

---

## 2. Technical Architecture, Workflows & Operational Methodologies

ic data, and able to model the ‘reachability’ of
customers, GIS is increasingly the basis of marketing
analytics to determine which customers can be profitably
connected to the network.
42
Discovery
Discovery applications are responsible for pulling in data
from the network for either immediate access or, more
commonly, storage in Inventory, GIS or other databases
for subsequent analysis. The discovered network view is
modeled as a topology, and it continuously updated as
information is gathered from the network.
While some applications have discovery capabilities built-
in, particularly if they address just a single technology or
an industry-standard network interface is available, in
most CSPs there are several different network
technologies from two or three different vendors.
The challenge Discovery meets is to interface to multiple
vendor’s devices, NEM or NMS systems, via different
interfaces, extracting data in varying formats. More
recently, this discovery function is often integrated with
orchestration which oversees the network topology
across multiple domains and multiple vendors.
Data goes through an extract, transform and load (ETL)
process, eventually being made available to the target
OSS application via a single interface and single data
format.
Federation
OSS processes are only as good as the data they have
available to them. Data represents an OSS view of the
world, describing networks, services, customers, future
trends and past events. Data is available directly from the
network (via a Discovery application) or in databases
belonging to Inventories and Monitoring applications.
There is certainly no shortage of data to be extracted
from communications networks, OSS and BSS systems.
But because data comes from many sources – different
OSS systems, network domains and network technologies
– it’s not immediately easy to work with. The data
content and format can vary considerably. The data may
be physically in different places. Access to the data will be
through a range of different APIs and database types.
The role of Federation is to bring this data together either
by duplicating dispersed data to a single convenient
database or by providing a consistent API to reach
through to multiple data sources. By using a combination
of these techniques, Federation can make large amounts
of data useable by OSS, often without the need to go
through the process of replacing these established data
sources or introducing additional Inventory solutions.
43
Analytics & Business
Intelligence
Data has been at the heart of OSS applications for years,
but the analytics capabilities have tended to be rigid –
fixed to support the primary propose of each application.
The ever-reducing cost of IT hardware has made
traditional data analytics platforms like data warehouses
much more affordable. Furthermore, the emergence of
Big Data platforms like Hadoop has further reduced the
cost in terms of money and time.
These generic (at least, not OSS-specific) analytics and
business intelligence platforms are now being deployed
within OSS for ad-hoc reporting purposes and data mining
to gain better understanding of the CSPs business.
Inventory, GIS, Discovery, Network Engineering data
sources, merged with customer data from BSS
applications offer tremendous opportunity to learn about
how the network is working and what keeps customers
happily paying their bills.
44
Planning
A CSP must be able to engage in strategic planning for
growth in customer traffic, and tactical planning to design
bespoke services or resolve performance issues.
When new technology becomes available, such as LTE,
the CSP must also be able to plan its roll-out and the
associated upgrade of the existing network.
Planning, more than any other operational task, considers
not just the network capacity and capabilities, but also
the cost, revenue potential, and reliability of the network.
Planning is ultimately responsible for ensuring that all
other operational tasks are following rules and policies
that ensure the CSP is building and running an efficient,
profitable network that meets the business’ strategic
objectives.
In the past, networks were relatively ‘static’. Device
functions were fixed; traffic routes were inflexible;
resources were allocated to specific services for the long
term. As such, planning a network was a relatively slow,
infrequent task carried out maybe every few months to
prepare budgets and schedule major works.
Increasingly, as network become

---

## 3. Specifications, Best Practices & Regulatory / Compliance Standards

networks and modern services are as much built
on servers, databases and applications as they are on
routers, packets and paths. So, in addition to being more
analytical, OSS must also branch out in to modelling data
centers and IT resources with as much sophistication as
they have modelled routers and switches in the past.
Network virtualization, and the use cases it enables,
means that protocols that once were fixed and
predictable are now flexible, and subject to change as
demands on the network change. This introduces a new
layer of control to the network. This control layer is
usually found in the software stack the CSP chooses when
deploying technologies like SDN and NFV. The control
layer provides a whole new point of integration for OSS,
which is a challenge in itself, because these software
stacks and their associated standards are yet to fully
mature.
More fundamentally, the control layer provides a means
of influencing how the network operates in near real
time, where in the past this operation was changed either
occasionally or entirely fixed by the device type deployed.
This breaks a lot of assumptions and processes currently
in use by CSP’s OSS. Assumptions that traffic-engineering
a data route is a hands-on process to be done once during
service provisioning; assumptions that when a device is
installed in the network, that it can’t almost instantly
double its capacity to handle traffic. Assumptions that
devices and service termination points stay in the same
place.
The old rules that OSS software and the CSP’s processes
were built on – hundreds or thousands of development
years of effort – have changed.
77
The future of OSS
is already here
There will be a significant change to the very DNA of
many OSS applications and a need to introduce, and
automate, new operational processes to meet a CSP’s
specific business objectives for their new network.
In the short term, as network virtualization is introduced,
there will be a temptation to use enterprise IT tools and
self-built tools, using network management APIs to fill in
the gaps, creating silos of just-good-enough OSS.
Single use, point solutions for managing new technology
inevitably are developed, in advance of being integrated
into a carrier grade OSS. Such Enterprise software and DIY
tools are fine in the early days, possibly the only option,
until the technology and services they support reach
carrier-scale and become common-place.
Such an approach will lead to disjoint operational decision
making and inefficient processes.
OSS took a big leap forward at the start of the 21st
century when inventory and service fulfilment
applications were able manage the complete stack of
physical, logical and service resources.
Learning from history, it’s important that CSPs have a
strategy for OSS change which is in-step with network
change.
The really good news is that more suppliers than ever are
focused on OSS. With the shift away from proprietary
hardware and protocols to software and virtualization,
the telco industry now sees its value coming from the
software stack, not the boxes. This has resulted in
traditional hardware vendors investing in OSS for their
next generation networks, and traditional OSS vendors
raising their game to maintain their leadership.
Truly integrated, carrier grade software takes time to
develop by the vendors and time to deploy by CSPs.
To paraphrase sci-fi author William Gibson – The future’s
already here, it’s just not been installed by the CSPs yet.

