---
chapter: false
next: 
prev: 
title: 2. Laptop Setup
weight: 20
---

## Objectives

In this lab you will configure your laptop for the workshop. By the end of the module you will have:

* A directory or folder to hold all the files required for your dispenser
* Installed and tested a device driver to communicate with the miicrocontroller
* Downloaded a command line utility to program (flashed) the microcontroller
* Have an open terminal or command prompt ready to issue commands

The microcontroller is programmed, or flashed, via a USB serial connection from a computer or laptop. Based on the microcontoller chipset, a specific driver is required.

{{% notice note %}}
Each persons laptop is unique and the general instructions may not work for a variety of reasons such as having a older version of the driver loaded, insufficient permissions to install, or older versions of Operating Systems. Please ensure that the checkpoint at the end has been completed prior to starting the next lab.
{{% /notice %}}

## Steps to Complete

Follow each step in order and use the *Open for detailed step-by-step instructions* if required.

### 1. Create Local Folder

Create a local folder called `cdd` that will contain all downloads and assets needed for the workshop. It is recommended to create this within your web browsers default download location. When asked to *download resource* X *to `cdd` folder*, save or move the files to that folder.

{{%expand "Open for detailed step-by-step instructions" %}}

1. Open a file browser for your operating system (Windows: Explorer, macOS: Finder) and navigate to the default download folder used by your web browser.
1. Create a folder named `cdd` within Downloads.
1. Leave the file browser open as we will be using it to move files around in later modules.
{{% /expand%}}

### 2. Download and Install Serial Driver

The microcontroller used in this workshop, the [ESP32-DevKitC](https://www.espressif.com/en/products/hardware/esp32-devkitc/overview) has a built-in Silicon Labs CP210x serial controller. In order for you laptop to communicate, download and install the [CP210x USB to UART Bridge VCP Drivers](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers) for your operating system. Follow the instructions *exactly*, you may be required to provide permissions to the driver and in some cases restart you laptop to complete the installation process.

{{% notice warning %}}
Use the installer specific to the *exact version* of your operating system. Using the wrong driver will not work and may make it difficult to install the proper version later.
{{% /notice %}}

{{%expand "Open for detailed step-by-step instructions" %}}

1. Open a browser window to the the [CP210x USB to UART Bridge VCP Drivers](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)  download page.
1. Download the software (the *Download VCP* link) for your operating system. If in doubt, please verify the version and read the release notes to confirm.
1. Once downloaded, follow the instructions to complete the installation of the driver.

Here are some tips for popular operating systems:

* Windows 10 - Unzip and use installer for either 32-bit or 64-bit. The VCP driver may have been installed by Windows Update, but using the SIlicon Labs provided driver will work with the ESP32-DevKitC.
* WIndows 7/8/8.1 - Use the default driver, *not* the serial emulation one. The VCP driver may have been installed by Windows Update, but using the SIlicon Labs provided driver will work with the ESP32-DevKitC. If the default driver does not work, you may try the other driver.
* macOS/OSX - Mount the DMG file, or use the legacy folder for OSX 10.9 or 101.10. **NOTE:** On MacOS 10.13 and later, the installation of the driver may be blocked. To unblock, open the System Preferences Security & Privacy pane and unblock the system extension. See [Apple Technical Note TN2459](https://developer.apple.com/library/archive/technotes/tn2459/_index.html) "User-Approved Kernel Extension Loading" for more information.

{{% /expand%}}

### Download and Install esptool.py

To interact with the microcontroller via the serial USB connection, there is a specific application used. [Follow the instructions](https://github.com/espressif/esptool) for your operating system to download and/or install the application. If installed correctly the command should accessible from any directory.

{{%expand "Open for detailed step-by-step instructions" %}}

1. Navigate to the [esptool.py](https://github.com/espressif/esptool) GitHub repository and scroll down to the installation instructions.
1. For your operating system, follow the instructions to install the python modules.

***Optional Tools***

If you are unable to install the esptool via the Espressif GitHub repository, there are optional versions available for different operating systems. Please note that these have not been tested, and there may be differences between the arguments referenced in the lab modules and the actual software.

* **macOS** - If you have [brew](https://brew.sh/) installed, you can install esptool via `brew install esptool`.
* **All Operating Systems** - [esptool-ck](https://github.com/igrr/esptool-ck) has compiled versions, please check the [releases](https://github.com/igrr/esptool-ck/releases) section.

{{% /expand%}}

### Open Command Line Interface and Test All Components

To interact with the microcontroller, you will be doing so from a terminal window (macOS and Linux) or a command prompt (Windows). Create a terminal window and change to the `cdd` directory you created. Verify that you can run the esptool command, and then verify when you connect just the ESP32 via the serial cable that a new serial device is created.

{{%expand "Open for detailed step-by-step instructions" %}}

1. For macOS or Linux, launch a terminal window, for Windows launch a command prompt.
    1. Windows - [Launch a cmd.exe (Command Prompt)](https://renenyffenegger.ch/notes/Windows/dirs/Windows/System32/cmd_exe/index).
    1. macOS -  + `Space` -> terminal.app
    1. Linux - `Control` + `Alt` + `T`
1. From the terminal window, run esptool and verify proper operation:

    ```bash
    $ esptool.py -h                                                                                                             
    usage: esptool [-h] [--chip {auto,esp8266,esp32}] [--port PORT] [--baud BAUD] 
        ...
    $
    ```
1. Monitor what serial ports are in use *before* connecting the ESP32.
    1. For Windows, [check the current COMx ports](https://superuser.com/questions/1059447/how-to-check-com-ports-in-windows-10). Note that as you connect and disconnect the ESP32, the COMx number may change for each connection.
    1. For macOS, `ls -l /dev/tty.*` will show the ports. You should *not* see a `tty.SLAB_USBtoUART` entry yet.
    1. FOr Linux, `ls -l /dev/tty.*` and note the port numbers.
1. Connect the ESP32, then run the same commands and look for a new addition. That will be the *port* you will use when flashing and monitoring the microcontroller.




{{% /expand%}}

## Checkpoints

Please ensure the following checkpoints are validated before moving on to the next module.

1. Folder `cdd` - Verify and note the location of the folder

1. Serial driver installed and tested - When the ESP32 is connected, the driver is working if a new serial port is created (/dev/tty.SLAB_USBtoUART or similar for macOS, a COMx port for Windows).



1. Command line window left open for other lab modules.

## (optional) Outcomes

Lead off with something like "so why did we do x, y, and z?