---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: 
next: 
prev: 
title: 4. MCU Setup & Test
weight: 40
---

## Objectives

This lab module will walk you through connecting the components to test the operation of the dispenser without having to build the entire dispenser at this time.

By the end of this module you will have:

* Installed all the components needed to test the operation of the dispenser firmware with the cloud backend.
* Have an understanding of what each component does.
* Be able to communicate with the microcontroller via your laptop.

{{% notice warning %}}
Building the dispenser takes up a lot of room. For now, just remove the parts mentioned below and leave the rest in the zip-top bag. Promise: You *will* build entire dispenser in a bit!
{{% /notice %}}

The LED Ring is controlled by the microprocessor, and is used to denote the status of the overall application. It is powered and controlled by microcontroller and the firmware you will compile and flash.

The Controller Board serves a few functions.

* It acts as carrier for microcontroller, and provides easy to use connectors for the other components being connected such as the LED Ring, external power, and the aquarium motor which will be installed later.
* It allows for either USB provided power to test (however there is not enough power to active the motor), or can be powered by an external battery, such as the 9V provided.
* It also helps anchor all the components into the final design build while still providing access.

## Steps to Complete

Follow each step in order and use the *Click to open for detailed step-by-step instructions* if required.

### 1. Remove the Components to Use

Remove these four components from the zip-top bag (you should already have the ESP32 microcontroller and USB cable out from earlier testing):

* ESP32 Microcontroller
* Controller Board
* Ring LED
* USB Cable (Type-A to Micro USB data and power)

<img src="/images/lab4_components.png" alt="Components" height="400"/>

### 2. Connect the LED Ring to the Controller Board

Install the LED Ring into the `WS2812` 3-pin connector on the Controller Board with the tab aligned with the connector slot.

<img src="/images/lab4_led_connected.png" alt="Connecting LED Ring to Controller" height="400"/>

{{%expand "Click to open for detailed step-by-step instructions" %}}

1. Hold the LED Ring cable's connector between your fingers.
1. Align the tab on the connector with the slot on the 3-pin `WS2812` labeled receptacle on the Controller Board.
1. With slight pressure, insert the connector until it is fully in.

{{% /expand%}}

### 3. Install the Microcontroller into the Controller Board

Align the microcontroller into the dual inline socket on the other side of the Controller Board, aligning the large metal square package with the `Motor A Motor B` text on the controller board. Make sure all pins on the ESP32 and the socket, then gently insert until all the way in.

<img src="/images/lab4_insert_esp32.png" alt="Inserting ESP32 into Controller Board" height="400"/>

{{% notice tip %}}
It is very easy to accidentally bend the pins on the microcontroller. Turn over the Controller Board with the socket facing up, and then with your other hand gently position the microcontroller pins into the holes. Once all are in place, gently apply pressure equally (center of microcontroller works best) to insert all the way in. If you accidentally install backwards, place a finger *underneath* one end of the microcontroller and apply pressure to lift slightly. The do the same on the other end and alternate back and forth until the microcontroller is out of the socket.
{{% /notice %}}

{{%expand "Click to open for detailed step-by-step instructions" %}}

1. Hold the Controller Board in one hand with the socket side (opposite of the LED Ring connection) facing up.
1. In your other hand hold the microcontroller and align the side with the large metal side with tab (antenna) to the Controller Board with `Motor A Motor B` text.
1. Align the pins on the microcontroller to the socket and lightly place. Ensure each pin is in a hole.
   <img src="/images/lab4_side_not_flush.png" alt="ESP32 Aligned, not Plugged In" height="400"/>
4. With gentle, even pressure, press the microcontroller in the socket until flush.
   <img src="/images/lab4_side_flush.png" alt="ESP32 Aligned, Fully Inserted" width="600"/>

{{% /expand%}}

### 4. Connect the Microcontroller to Your Laptop and Test Serial Communication

Insert the USB cable's Micro USB connector into the end of the microcontroller, and the Type-A connector into your laptop. The red LED on the microcontroller indicates power, and the LED Ring *may* light up. Next, check that the serial port tested in the *Laptop Setup* module is there. Next, use the serial monitoring software to connect to the serial port. Press the button to the left of the USB connection and verify you see text after each press. Exit your monitoring software.

<img src="/images/lab4_plugged_in.png" alt="Controller Plugged In" height="400"/>

{{% notice info %}}
A Micro USB to Type-A cable was provided. If your laptop only has Type-C connector and you have a Micro USB to Type-C cable, make sure that it supports *both* power and data connections. The workshop presenter may have Micro USB to Type-C cables to loan out.
{{% /notice %}}

{{%expand "Click to open for detailed step-by-step instructions" %}}

1. Insert the USB cable into the microcontroller, and then your laptop and verify that is had power via the red LED on the microcontroller. 
1. Use the serial monitoring tool to verify that the same serial port for your laptop still works. In some cases, especially in Windows, this value may change on each connection or if you use a different serial port.
1. Press the button to the left of the USB connection and verify you see text after each press. It should look similar to this:

    ```
    rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
    configsip: 0, SPIWP:0xee
    clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
    mode:DIO, clock div:2
    load:0x3fff0018,len:4
    load:0x3fff001c,len:6340
    load:0x40078000,len:11276
    load:0x40080000,len:6084
    entry 0x4008032c
    I (28) boot: ESP-IDF v3.1.3-13-g44a799c47 2nd stage bootloader
    I (28) boot: compile time 18:50:42
    I (28) boot: Enabling RNG early entropy source...
    I (34) boot: SPI Speed      : 40MHz
    I (38) boot: SPI Mode       : DIO
    I (42) boot: SPI Flash Size : 4MB
    I (46) boot: Partition Table:
    ```

1. Exit the monitoring program. You may leave the microcontroller attached if you like.
{{% /expand%}}

## Checkpoints

Please ensure the following checkpoints are validated before moving on to the next module.

1. The LED Ring and microcontroller are connected to the Controller Board.
1. The microcontroller has power when connected to your laptop.
1. You can see text via the serial monitoring tool.

## Outcomes

So why are we only installing a few pieces of the entire dispenser instead of building now? When doing embedded software development, it is easier to work with a development microcontroller kit and the accessories you will be controlling. Normally this would be done with a breadboard or some other development kit (devkit). However, for those that are not familiar with that process, using the minimum pieces now will allow us to continue testing up until we do incorporate the components into the overall dispenser.