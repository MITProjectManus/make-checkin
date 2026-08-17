# How to Build a Raspberry Pi Checkin Kiosk

Complete instructions for hardware assembly, OS configuration, and software installation for a Make: Checkin kiosk using a Raspberry Pi 4 and touchscreen.

## Version History

| Date | Notes |
|------|-------|
| 2025-06-01 | Incorporated Chris' original PDF notes |
| 2026-03-03 | Chris' SHED checkin station setup notes |
| 2026-03-07 | Oliver incorporates 2026-03-03 SHED notes |
| 2026-06-03 | Oliver adds systemd service launch method |
| 2026-08-17 | Revised and completed for make-checkin repo |

---

## Part 1: Hardware

### Bill of Materials

**Required:**

- [SmartiPi Touch 2 case](https://smarticase.com/collections/smartipi-touch-2/products/smartipi-touch-2) — portrait-orientation case for the Raspberry Pi board and 7" official touchscreen. Note: not compatible with the Raspberry Pi Touch Display 2.
- [Raspberry Pi Touch Display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/) — original 7" capacitive touchscreen, 800×480 resolution
- Raspberry Pi 4 board (any RAM configuration)
- USB-C power supply — 30W recommended (Pi 4 draws up to ~15W; original Touch Display draws up to ~7W)
- USB-C power cable
- MicroSD card — 16 GB minimum; **Samsung Pro Endurance** cards are strongly recommended (designed for continuous 24/7 operation in security cameras)
- USB HID OmniKey 5427CK card reader

**Optional — alternate case and display:**

- [SmartiPi Touch Pro 3 case](https://smarticase.com/collections/smartipi-touch-pro-3/products/smartipi-touch-pro-3) — supports the Raspberry Pi Touch Display 2 and provides slightly better port security; does not support portrait orientation as well
- [Raspberry Pi Touch Display 2](https://www.raspberrypi.com/products/touch-display-2/) — 7" capacitive touchscreen, 1280×720 resolution; Pi mounts directly to the back, good for 3D-printed enclosures or panel cutouts

**Optional — stand mounting:**

The SmartiPi Touch 2 case is VESA 75 compatible. The following parts make a compact stand using a cheap iPad stand:

- VESA 75 mounting adapter bracket (3D printable files in this repo)
- 3mm laser-cut acrylic adapter plate (constrains the square key from the stand; laser-cut acrylic is sturdier than 3D printed)
- iPad stand with removable spring-loaded bracket, such as [Maxonar iPad Stand Holder](https://a.co/d/05Q334Gu) — remove the iPad bracket and attach the acrylic plate and VESA adapter instead
- 4× M4 bolts, 25mm, socket or button head

### Assemble the Hardware

1. Mount the Raspberry Pi 4 board to the Raspberry Pi Touch Display using the ribbon cable and standoffs.
2. Seat the assembly into the SmartiPi Touch 2 case. The case has a slot for the ribbon cable and screw positions for both the display and the Pi.
3. Route the power cable. The case has a cable management clip.
4. If mounting to a stand, attach the VESA 75 adapter plate to the back of the case using M4 bolts, then attach to the stand.
5. Do not connect power yet — finish OS setup first, then connect the USB card reader and power up.

---

## Part 2: Operating System Installation

Use Raspberry Pi Imager to write a pre-configured OS image to the microSD card before inserting it into the Pi.

### Steps

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your Mac, PC, or Linux machine.
2. Insert the microSD card into your computer (it will be completely erased).
3. Launch Raspberry Pi Imager and configure the following:

**Device:** Select the Raspberry Pi 4 (or whichever board you are deploying).

**Operating System:** Select **Raspberry Pi OS (64-bit)** — the default recommended OS.

**Storage:** Select the microSD card.

4. Before writing, click the gear/settings icon to pre-configure the image:

| Setting | Value |
|---------|-------|
| Hostname | A unique name for this kiosk (use the registered Ethernet hostname if the Pi has one) |
| Username | `pi` |
| Password | See LastPass note "Raspberry Pi credentials" in folder "Shared-MIT Project Manus" |
| WiFi SSID | `MIT` |
| WiFi Password | `UYm5CN2jfA` |
| WiFi Country | US |
| Locale | Washington D.C. · America/New_York · Keyboard: us |
| Enable SSH | Yes (password authentication) |
| Enable Raspberry Pi Connect | Yes |

For Raspberry Pi Connect, use the shared Project Manus account:
- Username: `project-manus-itaccts@mit.edu`
- Password: See LastPass note "Raspberry Pi credentials" in folder "Shared-MIT Project Manus"

5. Write the image and eject the microSD card.

---

## Part 3: First Boot and System Configuration

### 3.1 First Boot

1. Insert the microSD card into the Pi.
2. Connect a USB keyboard if configuring directly on the Pi (you can also connect via SSH through Raspberry Pi Connect once it is on the network).
3. Connect the USB OmniKey card reader.
4. Power on the Pi.

The Pi will reboot several times as it applies its pre-configuration. Once at the desktop:
- You should see a popup confirming connection to the `MIT` WiFi network.
- You should see a popup for the `netplan-eth0` connection (this is the USB OmniKey card reader presenting as a USB Ethernet adapter).

### 3.2 Apply System Updates

Apply all available updates before continuing. This step matters — the image written by Raspberry Pi Imager may be several months out of date.

**If working directly on the Pi or via SSH:**

```bash
sudo apt update
sudo apt upgrade --autoremove
```

**If connecting remotely via Raspberry Pi Connect for the first time**, update rpi-connect first, as updates may disconnect the session:

```bash
sudo apt update
sudo apt install --only-upgrade rpi-connect
```

Wait for the Pi to reconnect in Raspberry Pi Connect, then run the full upgrade:

```bash
sudo apt upgrade --autoremove
```

The Pi may reboot after updates complete.

### 3.3 Disable the On-Screen Keyboard

If you are working directly on the Pi with a USB keyboard, disable the on-screen touch keyboard to prevent it from appearing during kiosk operation:

**Raspberry Pi Menu → Preferences → Control Centre → Display → On-screen Keyboard → Disabled**

### 3.4 Switch Display System from Wayland to X11

The checkin app requires X11 for fullscreen mode. Wayland is the default in current Raspberry Pi OS.

```bash
sudo raspi-config
```

Navigate: **6 Advanced Options → A7 Wayland → W1 X11** (Openbox running on X11)

Select **Finish** and **Yes** to reboot. The Pi will come back up running the Openbox window manager on X11.

### 3.5 Set the Session Manager

After rebooting into X11, open a terminal and set the session manager to lxe/lxsession:

```bash
sudo update-alternatives --config x-session-manager
```

Find `lxe` or `lxsession` in the list and enter its number, then press Enter.

### 3.6 Rotate the Display to Portrait Orientation

**Via the GUI:** Raspberry Pi Menu → Preferences → Control Centre → Screens → DSI-1 → Orientation → Right → Apply

Click **OK**. Rotate the physical device so the mouse tracking matches the new orientation.

Reboot to confirm the display comes up in portrait orientation before continuing.

### 3.7 Fix the Ethernet/OmniKey Conflict (Ethernet deployments only)

The OmniKey 5427CK card reader presents as both a USB HID device and a USB Ethernet adapter. When connected, the Pi defaults to the reader as `eth0` and disables the built-in Ethernet interface. The following commands pin each interface to the correct profile:

```bash
# Pin the existing profile to the real onboard NIC
sudo nmcli connection modify netplan-eth0 connection.interface-name eth0

# Give the OmniKey's USB-Ethernet interface its own profile
sudo nmcli connection add type ethernet con-name usb0-omnikey ifname usb0 ipv4.method auto connection.autoconnect yes

# Bring both up
sudo nmcli connection up netplan-eth0
sudo nmcli connection up usb0-omnikey
```

Verify the result:

```bash
nmcli device status
ip a show eth0
ip a show usb0
```

You should see `eth0` connected via `netplan-eth0` with a LAN IP from your DHCP server, and `usb0` connected via `usb0-omnikey` with an IP in the `192.168.63.x` range (the reader's local subnet).

### 3.8 Install Unclutter (Hide Mouse Cursor)

Install `unclutter` to automatically hide the mouse pointer after a few seconds of inactivity — it shouldn't be visible during normal kiosk operation.

```bash
sudo apt install unclutter
```

This also installs the `unclutter-startup` package. Verify that unclutter is configured to start with X11:

```bash
cat /etc/default/unclutter
```

`START_UNCLUTTER` should be set to `true`. If not:

```bash
sudo nano /etc/default/unclutter
# Set: START_UNCLUTTER="true"
```

---

## Part 4: Install the Checkin Application

### 4.1 Clone the Repository

```bash
cd ~
git clone https://github.com/MITProjectManus/make-checkin.git
```

This creates `~/make-checkin/` with all application files.

### 4.2 Install Dependencies

```bash
pip install --break-system-packages -r ~/make-checkin/requirements.txt
```

The only package that needs to be installed is `pyairtable` — all other dependencies are included in Raspberry Pi OS by default.

### 4.3 Create the Configuration File

The `config.py` file must be created locally for each kiosk — it is not in the repository.

```bash
cp ~/make-checkin/config-example.py ~/make-checkin/config.py
nano ~/make-checkin/config.py
```

Fill in all values:

- **`secrets`**: Airtable PAT, MIT People API credentials, MIT Card API credentials
- **`site`**: The `name` field must match exactly the makerspace name as it appears in Airtable
- **`question`**: Customize the survey question and answers for this location
- **`logs`**: Set an absolute path to a log file, or leave empty to disable file logging

See `config-example.py` for the full structure with field descriptions.

### 4.4 Test the Application

Run the application manually to verify the configuration is correct before setting up autostart:

```bash
~/make-checkin/make-checkin.py -H
```

The kiosk window should open. Tap a card and confirm it checks in and out correctly. Exit with **Alt+F4**.

---

## Part 5: Autostart Setup

### 5.1 Install the Launch Script

Copy the launch script from the repo and make it executable:

```bash
cp "~/make-checkin/setup/Raspberry Pi/launch-make-checkin.sh" ~/make-checkin-pi.sh
chmod 755 ~/make-checkin-pi.sh
```

The script sets `DISPLAY=:0`, disables the screensaver, disables display power management (so the screen never sleeps), and launches the app with the `-H` flag for the HID Omnikey reader.

### 5.2 Install the systemd Service

Copy the service file to the systemd directory:

```bash
sudo cp "~/make-checkin/setup/Raspberry Pi/make-checkin.service" /etc/systemd/system/make-checkin.service
```

Load and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable make-checkin
```

Reboot:

```bash
sudo reboot
```

After the reboot, the checkin application should launch automatically at startup.

**Verify the service is running:**

```bash
sudo systemctl status make-checkin
```

**Testing restart behavior:** Exit the app with **Alt+F4** — it should re-launch automatically after 30 seconds.

**To temporarily stop the service** (e.g., to work on the machine):

```bash
sudo systemctl stop make-checkin
```

Remember to restart it when done, or reboot if the overlay filesystem is enabled (see Part 6).

### 5.3 Update the X Session Autostart

Add the screensaver and display power management disable commands to the X session autostart file so they also apply to the desktop session (not just the launch script).

The autostart file location depends on your session configuration. Check which file exists:

```bash
ls /etc/xdg/lxsession/LXDE-pi/autostart
ls /etc/xdg/lxsession/rpd-x/autostart
```

Edit whichever file exists (create it if neither does):

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add the following lines (and comment out the `@xscreensaver` line if present):

```
# @xscreensaver -no-splash
@xset s 0
@xset -dpms
```

These lines are also provided in `setup/Raspberry Pi/autostart` in the repo for reference.

---

## Part 6: Enable the Overlay Filesystem

The overlay filesystem makes the SD card effectively read-only during normal operation, protecting it from corruption caused by sudden power loss — important for a kiosk that will be frequently hard-powered.

**Important:** After enabling the overlay filesystem, all changes made to the Pi while it is running (including code edits and config changes) will be lost on reboot unless the overlay is temporarily disabled first. Disable the service before making changes.

```bash
sudo raspi-config
```

Navigate: **4 Performance Options → P2 Overlay File System**

- **Would you like the overlay file system to be enabled?** Yes
- **Would you like the boot partition to be write-protected?** Yes

Select **Finish** and **Yes** to reboot.

After the reboot, the Pi should boot with the overlay filesystem active, the write-protected boot partition, and the checkin application launching automatically. The kiosk is now ready for deployment.

---

## Making Changes After Deployment

To make changes to a deployed kiosk with the overlay filesystem enabled:

1. Disable the overlay filesystem via `sudo raspi-config` → Performance Options → Overlay File System → No
2. Reboot
3. Make your changes (edit code, update config, etc.)
4. Re-enable the overlay filesystem via `sudo raspi-config`
5. Reboot

Alternatively, connect via SSH through Raspberry Pi Connect to make changes remotely, remembering to disable the overlay first.

---

## Appendix: Legacy Notes

These notes are preserved for historical reference. The main instructions above supersede them.

**2025-06-01 — From Chris PDF "Installing a Signin Kiosk"**

The original checkin kiosk used the [Airtable-Card-Checkin](https://github.com/MITProjectManus/Airtable-Card-Checkin) repository and launched via `/etc/xdg/lxsession/LXDE-pi/autostart` rather than via a systemd service. The autostart approach is still valid if preferred but the systemd service provides better restart handling (30-second automatic restart on exit) and cleaner logging via `journalctl`.

The old checkin app had fullscreen mode commented out and required manually editing `card-checkin.py` line 104 to re-enable it. The current `make-checkin.py` also has fullscreen commented out (line 101) pending a fix to work with Wayland.
