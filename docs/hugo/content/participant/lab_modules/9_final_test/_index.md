---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: 
next: 
prev: 
title: 9. Dispense a Drink!
weight: 90
---

## Objectives

Okay, this is the moment of truth. You have:

1. Setup your laptop to flash the dispenser.
1. From Cloud9 compiled the firmware specific for your dispenser. 
1. Flashed and tested the cloud capabilities and built up enough credits to operate.
1. Optionally built the dispenser and are ready to test.

With all that completed, let's dispenser a real liquid drink.

## Steps to Complete

Follow each step in order and use the *Click to open for detailed step-by-step instructions* if required.

{{% notice %}}
The following steps are if you are using your own dispenser. If you elect to use one of the pre-built ones, bring your microcontroller (the ESP32) to one of the pre-built stations. Be careful when removing from the controller board as its easy to bend the pins on the ESP32.
{{% /notice %}}

### Power On the Dispenser

After completing the build step, ensure there is liquid in the bottle, an empty cup underneath, then connect the 9 Volt battery instead of the USB cable for power. Wait until the dispenser is online by viewing the LED status. Now. from 6 inches or 6 feet away click _DISPENSE!_ to pour yourself a drink!

{{% notice tip %}}
If you wish to record this event for posterity, have someone else video you clicking _DISPENSE!_ and having the dispenser pour the drink. Workshop assistants are glad to be your personal videographer if needed!
{{% /notice %}}

If something does wrong or doesn't work, review the build steps from the previous lab, or ask a workshop assistant for help.

{{%expand "Click to open for detailed step-by-step instructions" %}}

. Ensure the dispenser unit is built and ready to go:
.. Liquid in the bottle
.. Top assembly securely screwed down and the output hose centered
.. An empty cup under the output hose
. Now connect the 9 Volt battery. This will provide power to the microcontroller and the aquarium motor.
. Wait for the dispenser to fully come online by waiting for the LEDs to sync to the same status in the webapp.
. Okay, with no physical connection between your laptop and the dispenser, click _DISPENSE!_ to pour yourself a drink! 
. If the dispenser didn't properly dispense a drink, perform some troubleshooting.
.. Did you hear the motor whir or make noise?
... Yes: Check that the cap is securely seated on the bottle, there may be a air gap.
... No: Check the connection from the motor to the control board (disconnect the 9V battery first)
.. If the LED ring change to the animated dispense pattern, verify there are enough credits and that the dispenser is online (toggle the LED)
.. You can also ask a workshop assistant for help in figuring out the problem.

{{% /expand%}}

## Checkpoints

There is only one checkpoint to verify, and that is you successfully dispensed a drink!

## Outcomes

Congratulations! You have successfully completed the _Connected Drink Dispenser_ workshop. We hope that you enjoyed the session and came away with a general understanding in how you can incorporate AWS IoT services into an overall multi-user or multi-tenant AWS workload.