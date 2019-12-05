---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: 
next: 
prev: 
title: 8. Build Dispenser
weight: 80
---

## Objectives

This module provides necessary steps to build and test your drink dispenser

## Steps to Complete

Follow each step in order and use the *Open for detailed step-by-step instructions* if required.

### Specific action to complete

1. Verify that you have all necessary parts:
    - Base plate
    - 1/2" PVC Cap (white)
    - 1/2"x1' PVC pipe (orange)
    - Top, middle (with LED ring), and bottom plates for top assembly
    - 8 M3-6mm 25mm standoffs
    - 9 M3 Cap nylon nuts
    - 4 M3-6mm nylon screws
    - 4 M3-8mm nylon screws
    - 2 M3-12mm stainless steel screws
    - 1 M3 hex nut
    - Pump motor
    - 9V battery
    - 9v battery clip with JST-2 connector
    - Electronics controller board
    - ESP32-DevKitC development board

    Consult with image below for the material list:

    ![DispenserParts.jpg](/images/lab8_materials.jpg)

1. Build base plate:

    ![BasePlate-s1.jpg](/images/lab8_baseplate.jpg)

1. Place M3x12mm stainless steel screw from inside of PVC cap as shown on the pictures below:

    ![BasePlate-s2.jpg](/images/lab8_baseplate_cap.jpg)

1. Thread it through the base plate hole closest to the edge and tighten with nylon cap nut from the bottom:

    ![BasePlate-s3.jpg](/images/lab8_attach_cap1.jpg)
    ![BasePlate-s4.jpg](/images/lab8_attach_cap2.jpg)
    ![BasePlate-s5.jpg](/images/lab8_attach_cap3.jpg)

1. Place the hex nut inside PVC cap and align to the both holes (PVC and base plate):

    ![BasePlate-s6.jpg](/images/lab8_attach_cap4.jpg)

1. Thread the M3x12mm stainless steel screw from the bottom and tighten (ask for help as this is the only step you will need a screwdriver):

    ![BasePlate-s7.jpg](/images/lab8_long_screw.jpg)

1. It should look like this:

    ![BasePlate-s8.jpg](/images/lab8_cap_complete.jpg)

1. Take M3x6mm screws(the shorter ones):

    ![BasePlate-s9.jpg](/images/lab8_short_screws.jpg)

1. Place them as show on the picture:

    ![BasePlate-s10.jpg](/images/lab8_base_screws_inserted.jpg)

1. Tighten them by hand using M3 cap nuts from the bottom:

    ![BasePlate-s11.jpg](/images/lab8_base_nuts.jpg)

That completes the base assembly, now to build the top assembly.

1. Build top assembly stating with the motor:

    ![TopAssembly-s1.jpg](/images/lab8_top1.jpg)

1. Insert the motor as shown on the picture (make sure of mounting slots!)

    ![TopAssembly-s2.jpg](/images/lab8_top2.jpg)

1. Insert the M3x8mm hex standoff screws (longer ones) as show on the picture:

    ![TopAssembly-s3.jpg](/images/lab8_top3.jpg)

1. Tighten the M3x6mm-25mm standoffs from the bottom (do not over tighten it):

    ![TopAssembly-s4.jpg](/images/lab8_top4.jpg)

1. Take the middle plate with mounted LED ring and make sure that orientation is correct:

    ![TopAssembly-s5.jpg](/images/lab8_led_ring1.jpg)

1. Attach 9 Volt batter cable's JST-2 connector (the small white connector at the end of the cable) to the JST-2 socket marked GND 9V. (Make sure you are not using LiPo socket!!!):

    ![TopAssembly-s6.jpg](/images/lab8_battery_cable1.jpg)
    ![TopAssembly-s7.jpg](/images/lab8_battery_cable2.jpg)
    
1. Assemble controller board, middle plate and top plate with motor as shown:

    ![TopAssembly-s8.jpg](/images/lab8_controller1.jpg)
    ![TopAssembly-s9.jpg](/images/lab8_controller2.jpg)

1. Attach pump motor cable to the pins on the controller board:

    ![TopAssembly-s10.jpg](/images/lab8_pump1.jpg)
    ![TopAssembly-s11.jpg](/images/lab8_pump2.jpg)

1. Place ESP32-DevKitC back on the controller board as in the earlier labs:

    ![TopAssembly-s12.jpg](/images/lab8_esp32.jpg)

1. Attach the other M3x6mm-25mm standoffs to secure motor and middle plate:

    ![TopAssembly-s13.jpg](/images/lab8_secure_motor.jpg)

1. Align controller board in the slots on the top and bottom plate, attach bottom plate, and secure with nylon M3 cap nuts

    ![TopAssembly-s14.jpg](/images/lab8_secure_controller.jpg)

1. Final result should look like this:

    ![TopAssembly-s15.jpg](/images/lab8_top_complete.jpg)

1. Thread vinyl tubes through bottle cap as shown. You might need to fold and squeeze the end of the tube to push it through:

    ![TopAssembly-s16.jpg](/images/lab8_tubing1.jpg)

1. Thread the larger vinyl tube from the bottom, middle plates to form a spigot and attach the smaller tube to the pump motor:

    ![TopAssembly-s17.jpg](/images/lab8_tubing2.jpg)

1. Very carefully insert 1/2" PVC pipe through top assembly (It is very tight to hold the top assembly by friction - ask for help if needed):

    ![TopAssembly-s18.jpg](/images/lab8_tubing3.jpg)

1. Fil the water bottle to 50-75% full. Then attach the bottle to the assembly (vertical so as not to spill water) and adjust height as needed (again, there will be a lot of resistance when moving, be careful!):

    ![TopAssembly-s19.jpg](/images/lab8_bottle1.jpg)
    ![TopAssembly-s20.jpg](/images/lab8_bottle2.jpg)

1. Your drink dispenser is ready and should look similar to this:

![TopAssembly-s21.jpg](/images/lab8_complete.jpg)

## Checkpoints

Please ensure the following checkpoints are validated before moving on to the next module:

- Both vinyl tubes are airtight on the bottle cap
- The orientation of your microcontroller
- 9V cable connected to socket marked GND 9V