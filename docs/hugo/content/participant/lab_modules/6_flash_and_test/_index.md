---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: 
next: 
prev: 
title: 6. Flash & Test MCU
weight: 60
---

## Objectives

In this lab module, you will complete the configuration of the dispenser firmware, download the compiled files to your laptop, and then use the tools to flash the microcontroller. At that point, the main components of the dispenser with the exception of the motor, will be fully operational. By the end of the module you will have:

* Modified the base firmware code to work with your specific account.
* Compiled and downloaded the code files to your laptop.
* Flashed the microcontroller with the compiled code on your laptop.
* Verified it is communicating with AWS IoT by turning on and off the LED.

## Steps to Complete

Follow each step in order and use the *Open for detailed step-by-step instructions* if required.

### Modify the Source Files for Your Dispenser

The X.509 client certificate and private key you downloaded earlier to your laptop's `cdd` directory uniquely identify your dispenser from all others. In order to communicate to AWS IoT core, you need to modify two of the source files in Cloud9 with the following in `device_firmware/demos/include`:

| Firmware Source File  | `#define` Statement in File | Content  |
|---|---|---|
| `aws_clientcredential.h` | clientcredentialMQTT_BROKER_ENDPOINT | AWS IoT Endpoint value from *MY DETAILS* section of webapp  |
| `aws_clientcredential.h` | clientcredentialIOT_THING_NAME | Your assigned dispenser name (3-digit number) to use when connecting to the MQTT broker  |
| `aws_clientcredential.h` | clientcredentialWIFI_SSID | WiFi network name provided by workshop presenter  |
| `aws_clientcredential.h` | clientcredentialWIFI_PASSWORD | Provided password for the WiFi network  |
| `aws_clientcredential_keys.h` | keyCLIENT_CERTIFICATE_PEM | Converted X.509 certificate (`nnn-certificate.pem.crt`)  content from <a href="https://cdd.baah.io/cred_formatter/index.html" target="_blank">Credential Formatter</a> |
| `aws_clientcredential_keys.h` | keyCLIENT_PRIVATE_KEY_PEM | Converted certificate private key `nnn-private.pem.key`  content from <a href="https://cdd.baah.io/cred_formatter/index.html" target="_blank">Credential Formatter</a> |

In Cloud9, navigate to the `device_firmware/demos/include` folder, then double-click on the two files above and modify the contents. The output for the last two PEM files in `aws_clientcredential_keys.h`, when copied over should look similar to this before and after (certifcate only, do the same with private key):

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

Once both files are modified, save them in the Cloud9 IDE, but leave them open to make changes if needed later.

{{%expand "Open for detailed step-by-step instructions" %}}

1. In Cloud9, navigate to the `device_firmware/demos/include` folder then double-click the two source files to modify:

    ![Source file to update](/images/lab6_c9_includes.png)

1. In each file reference above, replace the contents between the double-quotes. All values you need to replace start with `"REPLACE_WITH_..."`. Here are examples of what the WiFi and Certificate values should look like when done:

    **BEFORE**:
    ![Source files before update](/images/lab6_c9_mod_before.png)

    **AFTER**:
    ![Source files after update](/images/lab6_c9_mod_after.png)

{{% notice note %}}
The WiFi SSID must be entered exactly as given. Also, for the certificate and private key entries make sure the `---BEGIN` and `---END` look exactly as above. The data will be different and the private key will only be a few lines long as it is an ECC key.
{{% /notice %}}

1. For each file, click the tab the from the Cloud9 menu, save both files (*File->Save*). Leave both files open as it will be easier to correct and potential errors.

{{% /expand%}}

### Compile and Download the Code from Cloud9

With the updated files save, click on the terminal window where you did the compile steps in the previous lab. Run the `make` command again which will pick up the file changes and compile the firmware.

```bash
cd ~/environment/connected-drink-dispenser-workshop/device_firmware/build
make all -j4
```

Navigate in the Cloud9 file browser and open the `connected-drink-dispenser-workshop/device_firmware/build` folder. Scroll down and right-click on `aws_demos.bin` and select *Download* and save to your `cdd` directory. Do the same for the `build/bootloader/bootloader.bin` and `build/partition_table/partition_table.bin` files.

In your laptop's `cdd` directory you should have these three files.

{{%expand "Open for detailed step-by-step instructions" %}}

1. In Cloud9, click on the terminal window and rebuild the device firmware.

    ```bash
    cd ~/environment/connected-drink-dispenser-workshop/device_firmware/build
    make all -j4
    ```

    ![Update firmware build](/images/lab6_c9_build.png)

1. Right-click on `aws_demos.bin`, select *Download*, and save the file to your `cdd` directory. Do the same in the `bootloader` folder for `bootloader.bin`, and in `partition_table` for `partition-table.bin`.

    ![Download firmware](/images/lab6_c9_download.png)

1. When completed, make sure that `aws_demos.bin`, `bootloader.bin`, and `partition_table` are saved and available in your laptop's `cdd` directory.

{{% /expand%}}


### Flash and Monitor the Microcontroller from Your Laptop



Short description of what to do for experienced people

{{%expand "Open for detailed step-by-step instructions" %}}

detailed steps with markdown.
{{% /expand%}}

## Checkpoints

Please ensure the following checkpoints are validated before moving on to the next module.

## (optional) Outcomes

Lead off with something like "so why did we do x, y, and z?