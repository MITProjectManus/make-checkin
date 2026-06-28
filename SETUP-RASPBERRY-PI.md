# How to Build a Raspberry Pi Checkin Station

## Version History

* 2025-06-01 / Incorporated Chris' original PDF notes; these are now in Appendix AR1  
* 2026-03-03 / Chris creates a new Google Doc with SHED checkin station setup notes; these should be in this master document  
* 2026-03-07 / Oliver updates this document to incorporate 2026-03-03 Chris SHED notes; 2nd doc deleted
* 2026-06-03 / Oliver updates the instructions with a `systemd` service launch script

## Hardware - Building the Physical Kiosk

### Bill of Materials

* [SmartiPi Touch 2 case](https://smarticase.com/collections/smartipi-touch-2/products/smartipi-touch-2)
  * This is a vertical-orientation minimal case for a Raspberry Pi board and the 7" Raspberry Pi Display touchscreen
  * The case supports a vertical orientation well
  * This case is not compatible with the Raspberry Pi Touch Display 2
  * This case does not protect the ports on the Pi in environments where that might be a concern
* [Raspberry Pi Touch DIsplay](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)
  * 7" capacitive touchscreen, 800x480 resolution
* OPTIONAL: [SmartiPi Touch Pro 3 case](https://smarticase.com/collections/smartipi-touch-pro-3/products/smartipi-touch-pro-3)
  * This case is less streamlined but supports the Raspberry Pi Touch Display 2, as well as slighly better security by moving the Pi away from the display edge making it difficult to connect to ports without removing the case
  * This case does not support a portrait orientation as well
  * Consider if your available hardware requires it, or you need a little extra security for your environment
* OPTIONAL: [Raspberry Pi Touch Display 2](https://www.raspberrypi.com/products/touch-display-2/)
  * 7" capacitive touchscreen, 1280x720 resolution
  * The Pi can be mounted to the back of the display, so a good option if you 3D print your own enclosure or mount it into a panel cutout
* USB-C power supply
  * Consider about a 30W USB-C power supply if using a Raspberry Pi 4 and the original Raspberry Pi Touch Display
  * Maximum power draw for the Pi 4 is a little over 15W
  * Maximum power draw for the original Touch Display is about 7W
* USB-C power cable
* Mounting to a stand:
  * If you design your own wall or stand mounting, the case can mount to any VESA 75 plate
  * We use cheap iPad stands and remove the spring-loaded iPad bracket to instead attach a plate and a 3D printed VESA 75 adapter; this makes for a very compact final package, but requires a little fabrication work:
    * OPTIONAL: VESA 75 mounting adapter bracket (3D printable files in this repo) which locks in the Y adapter cable and allows you to mount to a cheap iPad stand
    * OPTIONAL: 3mm laser-cut acrylic adapter plate (can also be 3D printed but is used to constrain the square key from the stand, so laser cut acrylic will be sturdier)
    * OPTIONAL: iPad stand with removable spring-loaded bracket sich as [Maxonar iPad Stand Holder](https://a.co/d/05Q334Gu)
    * 4x 25mm M4 bolts (socket or button head) 

# FINISH EDITING

## Assemble the hardware

## Install and pre-configure Raspberry Pi OS on microSD card

* Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to your Mac, PC, or Linux machine  
* Procure a microSD card, with at least 16GB capacity (this will be erased completely); **Samsung Pro Endurance** cards are strongly recommended; endurance cards are designed for continuous operation in security cameras and field data recorders  
* Launch **Raspberry Pi Imager** and connect the microSD card to your computer  
* In Raspberry Pi Imager:  
  * Select the Raspberry Pi hardware board that will be deployed  
  * Select **Raspberry Pi OS (64-bit)** (this is the default recommended OS)  
  * Select the microSD media on your computer  
  * Enter the desired hostname of the checkin station; this name should be unique as it will appear in Raspberry Pi Connect; if the Pi is registered for Ethernet with a permanent hostname, use that one  
  * Set the correct localisation (Capital city: Washington, D.C.; Time zone: America/New York; Keyboard layout: us)  
  * Set the Raspberry Pi default account  
    * Username: pi  
    * Password: *See LastPass note "Raspberry Pi credentials" in folder "Shared-MIT Project Manus"*  
  * Set WiFi network parameters  
    * SSID: MIT  
    * Password: UYm5CN2jfA  
  * Enable SSH via username/password  
  * Enable Raspberry Pi Connect and generate its auth token  
    * For token generation use this shared Raspberry Pi Connect account:  
      * username: [project-manus-itaccts@mit.edu](mailto:project-manus-itaccts@mit.edu)  
      * password: *See LastPass note "Raspberry Pi credentials" in folder "Shared-MIT Project Manus"*  
  * Write the Raspberry Pi OS image to the microSD card  
  * Click "Finish" to exit Raspberry Pi Imager and eject the microSD card

## Boot and configure Raspberry Pi

* Insert the microSD card into the Raspberry Pi checkin station hardware  
* Connect a USB keyboard if completing the configuration directly on the Raspberry Pi (it can also be completed via SSH connecting through Raspberry Pi Connect once the the Pi is on the network)  
* Connect the USB MIT card reader  
* Power on the Raspberry Pi  
  The Raspberry Pi will reboot multiple times as it applies its pre-configuration and reboots into its configured state.  
* Once it boots into its configured state it will show the Raspberry Pi desktop  
  * You should see a popup message indicating the Pi has connected to the WiFi network "MIT"  
  * You should see a popup message indicating the Pi has connected to the Ethernet network "netplan-eth0" (this is the USB MIT card reader  
* The version of Raspberry Pi OS installed by Raspberry Pi Images is usually a little out of date; apply the latest updates via:  
  * Either by clicking on the updater icon (looks like a download arrow when updates are available) in the menu bar to run the GUI updater…  
  * or by opening a terminal window and running:  
    sudo apt update  
    sudo apt upgrade –autoremove  
  * The result will be the same. You can't over-update, so if you do both, that's okay too.  
  * Note: if you are setting the station up remotely via SSH through Raspberry Pi Connect, you cannot run the GUI updater; from the command line, run:  
    sudo apt update  
    sudo apt install \--only-upgrade rpi-connect  
    first to only update the Raspberry Pi connect software. Doing this will disconnect the Pi from Raspberry Pi connect. Once it re-appears in Raspberry Pi Connect, reconnect to it and run the remaining updates via sudo apt upgrade –autoremove  
  * Depending on the types of updates, the Pi may reboot after updates are complete  
* If working directly on the Pi with a USB keyboard, disable the on-screen touch keyboard via **Raspberry Pi Menu** \> **Preferences** \> **Control Centre**, then **Display**, and toggle **On-screen Keyboard** to "Disabled".  
* Run raspi-config to switch to the X11 window system which supports full-screen mode for Python applications  
  * Open a terminal window or connect via SSH / Raspberry Pi Connect  
  * Run sudo raspi-config  
  * Switch the GUI from Wayland to X11  
    * Select 6 Advanced Options  
    * Select A7 Wayland   
    * Select W1 X11 to switch to Openbox running on X11  
    * Select Finish and Yes to reboot when prompted  
    * The Pi will reboot into X11 and the Openbox window manager  
* Once back at the Desktop, open a terminal window and install the lxe xsession manager:  
  * sudo update-alternatives \--config x-session-manager  
  * Enter 1 and press \<enter\> to choose lxe / lxsession  
* Rotate the screen for vertical orientation  
  * Via the GUI: Raspberry Pi Menu \> Preferences \> Control Centre, then scroll down to Screens  
  * From the Screens menu select the primary screen, DSI-1, then Orientation, then Right  
  * Click Apply and Okay (be prepared to rotate the device so your mouse tracking matches the new orientaiton)  
* Optional: Reboot the Pi to make sure it comes up in the new display orientation and is ready for the checkin software installation
* Optional: if using with an **Ethernet connection** to the network, the following steps are needed to enable networking on the internal Ethernet interface:
  * Why? The USB HID OmniKey 5427CK Standard Reader in use at MIT presents as both a USB HID device to the Raspberry Pi (for simulated keyboard input from a card tap) and as a USB Ethernet adapter to allow connecting to the web server interface on the reader for configuration. In our setup the Pi will default to the card reader as `eth0` and disable the built-in Ethernet interface. The following commands will correctly set the built in Ethernet interface as the main one, leaving the card reader interface also active on a locally routed IP address.
  * Run the following at a terminal command prompt:

  ```
# Pin the existing profile to the real onboard NIC
sudo nmcli connection modify netplan-eth0 connection.interface-name eth0

# Give the OmniKey's USB-Ethernet gadget its own profile
sudo nmcli connection add type ethernet con-name usb0-omnikey ifname usb0 ipv4.method auto connection.autoconnect yes

# Bring both up
sudo nmcli connection up netplan-eth0
sudo nmcli connection up usb0-omnikey
  ``` 

  * To verify that the changes took:

  ```
nmcli device status
ip a show eth0
ip a show usb0
  ```

  * You should see `eth0` connected with `netplan-eth0` and an IP from your LAN's DHCP server, and `usb0` connected with its own profile, with an IP that looks like `192.168.63.x` for the reader.

## Install the checkin Python application

* Open a terminal window and fetch the most recent version of the Python application:  
  cd \~  
  git clone [https://github.com/MITProjectManus/Airtable-Card-Checkin.git](https://github.com/MITProjectManus/Airtable-Card-Checkin.git)  
* This will create the directory **Airtable-Card-Checkin** in the home directory and populate it with the application files  
* Install requirements  
  * **NOTE:** The original requirements.txt file has way too many things in it, and also needlessly locks in version numbers. The only package that is not already installed is "pyairtable" and the version number is not necessary; edit requirements.txt to only contain the line "pyairtable", then run:  
  * pip install –break-system-packages \-r requirements.txt  
* **NOTE:** The old Python application has the flag to launch in fullscreen mode or in window mode hard-coded in the application, and Chris' last commit has it commented out so it does not launch in fullscreen mode; edit [card-checkin.py](http://card-checkin.py) and on line 104 remove the leading comment hash.  
* Create a bash launch script  
  * The old Python application does not include the bash launch script. Create \~/[checkin.sh](http://checkin.sh) and incude the following commands:  
    * \#\!/bin/bash  
    * export DISPLAY=:0  
    * xset s 0  
    * xset \-dpms  
    * /home/pi/Airtable-Card-Checkin/card-checkin.py \-H  
  * These commands will:  
    * Set the DISPLAY environment variable so the Python app displays on the main screen no matter how it is launched  
    * Set the screensaver timeout to 0 which disables it  
    * Disable Display Power Management Signaling (DPMS) to never sleep the display  
    * Launch the Python application; the \-H flag tells it to use the HID card reader  
  * Run  
    * chmod 755 \~/checkin.sh to make the file executable  
* You can now launch the checkin application by running \~/checkin.sh from a shell prompt to check that everything is working correctly

## Create a systemctl service

To make sure the checkin application is always running, we will create and install a launch script and register it with systemctl.

### Create launch script /etc/systemd/system/checkin.service and add:

\[Unit\]  
Description=Tap Checkin Python Application  
After=graphical.target  
Wants=graphical.target

\[Service\]  
User=pi  
Environment=DISPLAY=:0  
Environment=XAUTHORITY=/home/pi/.Xauthority  
WorkingDirectory=/home/pi/  
ExecStart=/home/pi/checkin.sh  
\# Below could also be "on-failure" to only restart if it exits with a code  
Restart=always  
RestartSec=30

\[Install\]  
WantedBy=graphical.target

### Load and enable the service

* Run sudo systemctl daemon-reload to reload system manager configuration  
* Run sudo systemctl enable checkin to enable the service at startup  
* Reboot the pi and the checkin application should now launch on startup  
* Exit the checkin application with ALT-F4 and it should re-launch after 30 second  
* **NOTE:** To disable the application, for example to work on the machine, run sudo systemctl stop checkin. While working on the machine later, remember that changes are temporary if you are running with the overlay filesystem and write-protected boot partition enabled, which we will do in the next step.

## Update X session autostart

Update the X session autostart file to also run the two xset commands and to disable automatic launching of xscreensaver if that is enabled.

* autostart file has moved to `/etc/xdg/lxsession/rpd-x/autostart`
* Comment the `@xscreensaver...` line if present
* Add:
  * `@xset s 0`
  * `@xset \-dpms`

## Configure the Overlay Filesystem

* Run raspi-config via sudo raspi-config in the Terminal  
* Enable the overlay filesystem  
  * Select "4 Performance Options"  
  * Select "P2 Overlay File System"  
  * Would you like the overlay file system to be enable? **Yes**  
  * Would you like the boot partition to be write-protected? **Yes**  
  * Select "Finish"  
  * Select "Yes" to reboot now  
* If everything went well, you should now be booted into a kiosk Raspberry Pi with a write-protected SD card (making it safe to powercycle) and the checkin application auto-launched.

# Appendices

## Appendix AR1: Archive/Legacy

**2025-06-01 From Chris PDF "Installing a Signin Kiosk"**  
These instructions are out of date 

* Install Raspberry Pi OS  
  * Do updates  
    * sudo apt update  
    * sudo apt upgrade  
    * sudo apt autoremove  
  * Switch to X11  
  * Activate VNC  
  * Activate Raspberry Pi Connect  
  * sudo update-alternatives \--config x-session-manager (switch to lxe, option 1\)  
  * Switch screen orientation to “Right” (do for display and then select touchscreen)  
* Copy over the code  
  * usually grab the release from git  
  * Make sure we’re running in fullscreen mode  
* Install dependancies  
  * pip install \--break-system-packages \-r requirements.txt  
* Install unclutter  
  * sudo apt install unclutter  
  * This should also install the dependent package unclutter-startup  
  * Verify that unclutter is set to start on X11 launch via cat /etc/default/unclutter  
  * START\_UNCLUTTER should be set to true. If not edit the file and include START\_UNCLUTTER="true"  
  * Reboot and the mouse pointer should now disappear after a few seconds of no movement  
* Install a secrets.py file  
* Create checkin-bash \~/checkin.sh  
  \#\!/bin/bash  
  \# Run this script in display 0 \- the monitor  
  export DISPLAY=:0  
  \# Hide the mouse from the display  
  unclutter &  
  xset s 0  
  xset \-dpms  
  \# Run checkin program  
  Airtable-Card/card-checkin.py \-H  
* Add checkin script execution to /etc/xdg/lxsession/LXDE-pi/autostart  
  * This superseeds the pi.desktop below  
* ~~Edit .config/autostart/pi.desktop (2/20/2025 \- skip this, see below)~~  
  ~~\[Desktop Entry\]~~  
  ~~Type=Application~~  
  ~~Name=Checkin~~  
  ~~Exec=/home/pi/checkin-bash~~  
  ~~X-GNOME-Autostart-enabled=true~~

\======  
Notes 1/16/2025 (3/3/2025 incorporated into the main instructions)  
Be sure to switch to X11  
Do this first, before changing screen orientation.  
sudo update-alternatives \--config x-session-manager (switch to lxe, option 1\)  
Add checkin script execution to /etc/xdg/lxsession/LXDE-pi/autostart