---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: <i class="fas fa-user-graduate"></i>&nbsp;
next: 
prev: 
title: Lab Modules
weight: 10
---

## Individual Module Overview

There are various modules to complete in this workshop. Each module has a specific set of objects to complete, with the overall goal of the workshop being for you to build, program, and be able to dispense a drink. Each module is laid out in a similar manner:

* **Objective**<br/>A short explanation of *what* you will be accomplishing, and *why*.
* **Steps**<br/>Both high-level steps to complete the module, and a twirl-down with specific step-by-step instructions
* **Checkpoint**<br/>A completed list of what comes from the objectives that needs to be validated before moving on to the next steps.
* **Outcomes** (optional)<br/>Depending upon the module, this section describes how the steps taken above help for the workshop or general AWS IoT development patterns.

## Workshop Module List

These are the labs to complete in order:

TODO: Complete each bullet point lab

1. ~~Workshop overview and diagrams - Gavin - Understand relationship of user to dispenser, and AWS components used~~ - completed
1. ~~Local laptop setup - Gavin - Install serial drivers and software to flash and monitor connected ESP32~~ - completed
1. ~~Create workshop user account - Gavin - Create account, log in, download and describe user details section~~
1. Build ESP32 + Carrier - Anton - Install ESP32 into carrier, connect via USB to laptop, verify monitor command works. This time will allow C9 to complete
1. Build C9 development environment and compile code - Anton - Clone repo and the pull in ESP IDP components to dispenser code, build code, download
1. Flash and test - Anton - Verify that ESP32 starts up, connects, and provides validation of shadow. If not, move back to previous lab with hints
1. Investigate app and AWS account - Gavin - From console, IoT subscribe to shadow then click on LED on/off/toggle, view operations. Click on dispense (with $1), note change of Neo pixel LEDs. Share the love and build up at least $1/$2 in credits.
1. Build the dispenser - Anton - Complete hardware build with explanation of how different components work, and why.
1. Test - Gavin - Use their dispenser or optionally pre-built ones. 


{{% children description="true"   %}}