---
chapter: false
pre: <i class="fas fa-user-graduate"></i>&nbsp;
next: 
prev: 
title: Workshop Participant
weight: 10
---

## Welcome Workshop Participant!

The Connected Drink Dispenser, or CDD, simulates a fleet of physical devices managed and controlled by a cloud-based architecture. The physical device, which you will build, can dispense a drink from a standard bottle such as soda or water through an controlled air-pump, and uses an ESP32 microcontroller (MCU) as the brains of the operation. Connectivity to AWS IoT is done through a Wi-Fi network connection, and interaction and local device control is performed by an Amazon FreeRTOS application running on the MCU.

<img src="/images/lab2_esp32_connection.png" alt="ESP32 Microcontrollert" height="400"/>

To simulate dispenser activities, a web application (webapp) with user authentication is used. It can control dispensing a drink via the dispenser associated with the user, and to provide credits to other dispensers. This demonstrates how devices can be *scoped down* to limited permissions and actions, while still taking advantage of robust serverless applications.

<img src="/images/lab1_cloud_overview.png" alt="Cloud Architecture" width="70%"/>

## Using This Documentation

This section of the document covers the exercises you will be working through to completed the workshop. There are few things to note while walking through the modules:

* **Modules build on each other** - Please ensure that each module is completed in-order, and if there are checkpoints at the end, each is complete and operational. Do not move onto the next lab until this is validated. If you do have any questions, please raise you hand for support.

* **Comprehension over completion** - Each module will start with a set of objectives, a step-by-step walk through on *how* to complete. Besides the *how*, there will be a set of *why* takeaways which will be helpful in the future when using these skills.

* **Lab context** - Some modules be more of seeing what happens when certain operations that place. These will be put into context for the overall architecture of the Connected Drink Dispenser workshop.

You can navigate either from the menu to the left, or by using the blue navigation arrows (<span style="color:blue"><</span> and <span style="color:blue">></span>) to move forward or back a page.

Let's get started by navigating *forward* to *Activities Page*!