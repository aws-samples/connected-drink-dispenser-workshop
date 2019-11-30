---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: 
next: 
prev: 
title: 6. Develop, Flash, & Test MCU
weight: 60
---

## Objectives

In this lab module, you will complete the configuration of the dispenser firmware, download the compiled files to your laptop, and then use the tools to flash the microcontroller. At that point, the main components of the dispenser with the exception of the motor, will be fully operational. 

By the end of the module you will have:

* Modified the base firmware code to work with your specific account
* Compiled and downloaded the code files to your laptop
* Flashed the microcontroller with the compiled code on your laptop
* Verified it is communicating with AWS IoT by turning on and off the LED

## Steps to Complete

Follow each step in order and use the *Click to open for detailed step-by-step instructions* if required.

### Modify the Source Files for Your Dispenser

The X.509 client certificate and private key you downloaded earlier to your laptop's `cdd` directory uniquely identify your dispenser from all others. In order to communicate to AWS IoT core, the firmware must be configured with this information. To do so, you need to modify two of the source files in in `device_firmware/demos/include` with the following:

| Firmware Source File  | `#define` Statement in File | Content  |
|---|---|---|
| `aws_clientcredential.h` | clientcredentialMQTT_BROKER_ENDPOINT | AWS IoT Endpoint value from *MY DETAILS* section of webapp  |
| `aws_clientcredential.h` | clientcredentialIOT_THING_NAME | Your assigned dispenser name (3-digit number) to use when connecting to the MQTT broker  |
| `aws_clientcredential.h` | clientcredentialWIFI_SSID | WiFi network name provided by workshop presenter  |
| `aws_clientcredential.h` | clientcredentialWIFI_PASSWORD | Provided password for the WiFi network  |
| `aws_clientcredential_keys.h` | keyCLIENT_CERTIFICATE_PEM | Converted X.509 certificate (`nnn-certificate.pem.crt`)  content from <a href="../../../cred_formatter/index.html" target="_blank">Credential Formatter</a> |
| `aws_clientcredential_keys.h` | keyCLIENT_PRIVATE_KEY_PEM | Converted certificate private key `nnn-private.pem.key`  content from <a href="../../../cred_formatter/index.html" target="_blank">Credential Formatter</a> |

In Cloud9, navigate to the `device_firmware/demos/include` folder, then double-click on the two files above and modify the contents. The content of the `aws_clientcredential_keys.h` file should look similar to the following before and after copying the converted content of the two PEM files:

**BEFORE**:
```
#define keyCLIENT_CERTIFICATE_PEM                   "REPLACE_WITH_CONVERTED_CERTIFICATE_STRING"
```

**AFTER**:
```
#define keyCLIENT_CERTIFICATE_PEM                   "-----BEGIN CERTIFICATE-----\n"\
"MIICxjCCAa6gAwIBAgIVAJhkG3c6wT05SEZKJ3OsVHrQov6nMA0GCSqGSIb3DQEB\n"\
...
"IdbvOv7LLT9BD2Z8Mx9H/BhCd9ylpZEyQcl948GjEXgBDGdxUKFhrEfx\n"\
"-----END CERTIFICATE-----" 
```

Ensure that you update both the Certificate and Private Key sections. Leave the rest as-is.

Once both files are modified, save them from the Cloud9 IDE. You can leave the tabs open to quickly go back to the files if needed.

{{%expand "Click to open for detailed step-by-step instructions" %}}

1. In Cloud9, navigate to the `device_firmware/demos/include` folder then double-click the two source files to modify:

    ![Source file to update](/images/lab6_c9_includes.png)

1. In each file reference above, replace the contents between the double-quotes. All values you need to replace start with `"REPLACE_WITH_..."`. For all values except *keyCLIENT_CERTIFICATE_PEM* and *keyCLIENT_PRIVATE_KEY_PEM*, you can simply copy and paste the value.

1. For the *keyCLIENT_CERTIFICATE_PEM* and *keyCLIENT_PRIVATE_KEY_PEM* values, use the <a href="../../../cred_formatter/index.html" target="_blank">Credential Formatter</a>, the for **PEM Certificate or Key** browse to the downloaded certificate and private key (do each separately), then click on the *Display formatted PEM string to be copied into aws_clientcredential_keys.h*. That will display all the lines to replace for *keyCLIENT_CERTIFICATE_PEM* and *keyCLIENT_PRIVATE_KEY_PEM* respectively.

    Here are examples of what the WiFi and Certificate values should look like when done:

    **BEFORE**:
    ![Source files before update](/images/lab6_c9_mod_before.png)

    **AFTER**:
    ![Source files after update](/images/lab6_c9_mod_after.png)

{{% notice note %}}
The WiFi SSID must be entered exactly as given. Also, for the certificate and private key entries make sure the `---BEGIN` and `---END` look exactly as above. The data will be different and the private key will only be a few lines long as it is an ECC key.
{{% /notice %}}

1. For each file, click the tab the from the Cloud9 menu, save both files (*File->Save*). Leave both files open as it will be easier to correct any potential errors.

{{% /expand%}}

### Compile and Download the Code from Cloud9

After saving the updated files, click on the terminal window where you did the compile steps in the previous lab. Run the `make` command again which will pick up the file changes and recompile the firmware.

```bash
cd ~/environment/connected-drink-dispenser-workshop/device_firmware/build
make all -j4
```

In the Cloud9 file browser navigate to the `connected-drink-dispenser-workshop/device_firmware/build` folder and expand it. Scroll down and right-click on `aws_demos.bin` and select *Download* and save to your `cdd` directory. Do the same for the `build/bootloader/bootloader.bin` and `build/partition_table/partition_table.bin` files.

In your laptop's `cdd` directory you should now have these three files.

{{%expand "Click to open for detailed step-by-step instructions" %}}

1. In Cloud9, click on the terminal window and rebuild the device firmware.

    ```bash
    cd ~/environment/connected-drink-dispenser-workshop/device_firmware/build
    make all -j4
    ```

    ![Update firmware build](/images/lab6_c9_build.png)

1. In the Cloud9 file browser navigate to the `connected-drink-dispenser-workshop/device_firmware/build` folder and expand it.

1. Right-click on `aws_demos.bin`, select *Download*, and save the file to your `cdd` directory. Do the same in the `bootloader` folder for `bootloader.bin`, and in `partition_table` for `partition-table.bin`.

    ![Download firmware](/images/lab6_c9_download.png)

1. When completed, make sure that `aws_demos.bin`, `bootloader.bin`, and `partition_table` are saved and available in your laptop's `cdd` directory.

{{% /expand%}}


### Flash and Monitor the Microcontroller from Your Laptop

The final step in the modify->build->download->flash sequence is to flash the microcontroller. Connect the microcontroller to your laptop. Next, from the command prompt or terminal opened earlier, ensure you are in the `cdd` directory and then use *esptool* to flash.

{{% notice note %}}
The command `esptool ...` will be used. Note the syntax that works for *your* laptop installation (e.g., `./esptool.py`, etc.).
{{% /notice %}}

Run the flashing program replacing the `--port` with your value (default for macOS used below).

```
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 bootloader.bin 0x20000 aws_demos.bin 0x8000 partition-table.bin
```

You should see output similar indicated the firmware was flashed.

```
esptool.py v2.8
Serial port /dev/tty.SLAB_USBtoUART
Connecting........__
Chip is ESP32D0WDQ5 (revision 1)
Features: WiFi, BT, Dual Core, Coding Scheme None
Crystal is 40MHz
MAC: 24:0a:c4:23:d6:5c
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 921600
Changed.
Configuring flash size...
Auto-detected Flash size: 4MB
Compressed 24272 bytes to 14397...
Wrote 24272 bytes (14397 compressed) at 0x00001000 in 0.2 seconds (effective 1140.8 kbit/s)...
Hash of data verified.
Compressed 860384 bytes to 529993...
Wrote 860384 bytes (529993 compressed) at 0x00020000 in 8.0 seconds (effective 859.5 kbit/s)...
Hash of data verified.
Compressed 3072 bytes to 118...
Wrote 3072 bytes (118 compressed) at 0x00008000 in 0.0 seconds (effective 3733.3 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

At this point the microcontroller will reset and your code will be running on it! To verify that the process was performed correctly, start your serial monitoring program (*PuTTY* or *screen*). Reset the microcontroller via the button right to the Micro USB connector, and view the output. A properly configured microcontroller will have an *I (nnn) WIFI: SYSTEM_EVENT_STA_CONNECTED* message indicating it connected to the WiFi network, and then *\[ShadowTask\]* operations with *SUCCESS*, indicating that it is communicating with AWS IoT.

If you need to correct any errors in the firwmare, ensure to exit your *screen* session (`Ctrl-a`+`Ctrl-\`) alt close the console window in PuTTY before re-flashing it since the serial port can only be used by one process at the time.



{{%expand "Click to open for detailed step-by-step instructions" %}}

1. Connect the microcontroller to your laptop and ensure the red LED is lit and that the serial port is available.
1. From your command prompt or terminal in the `cdd` directory, flash the microcontroller with *esptool*.

    ```
    esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 bootloader.bin 0x20000 aws_demos.bin 0x8000 partition-table.bin
    ```

    Look for the *Hash of data verified* messages.

1. macOS/Linux: Start your serial monitoring program screen and connect to the microcontroller. Press the reset button to the left of the USB connector and nearest the red LED. Look for startup text containing *I (nnn) WIFI: SYSTEM_EVENT_STA_CONNECTED* and after a short time, *\[ShadowTask\]* operations with *SUCCESS*.

    ```
    ### <--- Comments, not part of microcontroller output
    ### First messages
    rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
    configsip: 0, SPIWP:0xee
    clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
    mode:DIO, clock div:2
    load:0x3fff0018,len:4
    load:0x3fff001c,len:6372
    load:0x40078000,len:11684
    ho 0 tail 12 room 4
    load:0x40080000,len:6112
    entry 0x40080330
    I (30) boot: ESP-IDF v3.1.5-105-g7313c836a5 2nd stage bootloader
    I (30) boot: compile time 23:19:39
    I (30) boot: Enabling RNG early entropy source...
    # WiFi startup
    2 7 [main] Connecting to network
    I (284) wifi: wifi driver task: 3ffbb758, prio:23, stack:3584, core=0
    I (284) system_api: Base MAC address is not set, read default base MAC address from BLK0 of EFUSE
    I (284) system_api: Base MAC address is not set, read default base MAC address from BLK0 of EFUSE
    I (304) wifi: wifi firmware version: 3c46a62
    I (1554) wifi: connected with SSID_NAME, channel 1
    I (1554) wifi: pm start, type: 1
    # !!! Look for this
    I (1554) WIFI: SYSTEM_EVENT_STA_CONNECTED
    # Connection to AWS IoT Core and successful communication with the device shadow
    54 985 [ShadowTask] [INFO ][MQTT][9850] (MQTT connection 0x3ffb6208) MQTT PUBLISH operation queued.
    55 1006 [iot_thread] [INFO ][Shadow][10060] Shadow UPDATE of 100 was ACCEPTED.
    56 1006 [ShadowTask] Successfully performed update.
    57 1006 [ShadowTask] Free mem: 129952
    ```

    NOTE: The *screen* command will take full control of the terminal. The fully exit, use the `Ctrl-a`+`Ctrl-\` to kill all windows. You can also use your arrow keys to navigate up by entering `Ctrl-a`+`ESC`. There are good [primers](https://linuxize.com/post/how-to-use-linux-screen/) on how to use *screen*.

1. Leave the microcontroller and the LED Ring connected for the next module.

{{% /expand %}}

## Checkpoints

Please ensure the following checkpoints are validated before moving on to the next module.

* Firmware build with no errors in Cloud9
* You downloaded and flashed the firmware with no errors
* You can monitor and see the dispenser connect to the WiFi network and establish a successful session to AWS IoT Core
* You have left the microcontroller connected for the next lab

## Outcomes

In this lab we went through all the normal steps of firmware development--albeit as all manual steps. The process is similar to normal software development where you write code, compile, debug, and then repeat. In the case of firmware development, especially when working with hardware peripherals, the added step is flashing the firmware to development board.

While Cloud9 is a fully integrated development environment, we only used it to edit and build the firmware, and have not taken full advantage of its capabilities.

While we used manual processes to illustrate the various steps, we would normally automate and use specific tools to make the development process more streamlined, consistent, and to reduce errors. All of the steps completed manually can be automated. In a more automated environment, the development process could operate in this manner:

1. Developer uses local IDE with integrated test and debugging tools (non-physical) to write code, commits to source control
1. Source control commit triggers AWS CodeBuild with toolchain image to compile code and update the `.bin` files to an Amazon S3 bucket.
1. Local workstation with attached hardware receives notice of new firmware, downloads, and flashes to microcontroller.
1. Local workstation places serial or debugger ports into monitor mode, resets the microcontroller and it runs through it's test.
1. Monitor output reviewed by developer to make next set of changes or corrections.

By understanding what the development process looks like in this lab module, you can automate any series of steps slowly to add consistency and repeatability to your development processes. 

