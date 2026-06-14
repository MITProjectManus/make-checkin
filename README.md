# Make: Checkin

A major new version of a card tap checkin kiosk program in Python able to run on Raspberry Pis (and other hardware) that processes MIT ID card taps (and digital ID taps) to check users into and out of makerspaces. This replaces [Airtable-Card-Checkin](https://github.com/MITProjectManus/Airtable-Card-Checkin), the original prototype version of card tap checkin for MIT makerspaces.

## Installation

Combine installation, configuration, and setup into one section that makes sense.

## Configuration

### Location `config.py` (not tracked)

For each location kiosk, the file `config.py` contains API keys and location-specific configuration items. This file needs to be locally managed and deployed for each kiosk. This file is **NOT** tracked and is excluded via `.gitignore`. For an example without keys see `config-example.py`.

### Hardware and Software Setup

For our current standard checkin kiosk hardware, a Raspberry Pi 4 with touchscreen and HID card reader, see the setup instructions for both hardware and software in the file:

SETUP-RASPBERRY-PI.md

## Troubleshooting

Add troubleshooting information here.

## Running List of Issues and Needed Enhancements

1. Sometimes stuck on "One moment..." screen; possibly if invalid data is read with card tap, or if network connection is lost on the Pi temporarily
2. Ignoring follow-up question will block forever on that screen until someone picks one; should time out and complete checkin
3. Better error checking, run state health monitoring, and recovery; most errors and blocking states are silent or logged in the background; should have a way of showing error to user, possibly watchdog timer for restart if an unrecoverable blocking state can occur
4. Network status and connection to APIs and internet are not shown; should indicate if no network, and retry periodically; should indicate if API endpoints are unreachable and retry periodically
5. A failure response from the MIT Card API should be indicated to the user, including token read from card and API error code
6. Performance is slow, better on the Pi 4 than the Pi 3, but probably could be improved with more compact API calls, fewer open ended searches, maybe local caching of info
7. Only MIT IDs can be read at the moment; should be able to register a tap ID (such as MiFare ID) in Airtable and check that if MIT ID read is invalid
8. Are we clearing the input buffer before the next card read?
9. Better idle and button graphics
10. Consider switching to normal landscape orientation for kiosks and checkin stations, avoiding display rotation issues; portrait is a nice stylistic option but does not have any functional benefits and requires several extra configuration steps; will require updating the code to deal with screen dimensions and layout more flexibly
11. Update code for fullscreen to work with Wayland, avoiding the need to switch to X11; there is no intrinsic reason a Tkinter app shouldn't run in fullscreen on Wayland, especially on newer Pis  
12. Investigate whether there is a touch input library for Tkinter
13. Consider switching to guizero (a simplified GUI library over Tkinter) for ease of maintenance by non-programmers; it has a simpler event loop and configuration model
14. DONE: Simplify requirements.txt \- most of the listed requirements are installed by default; the only post-installation package install needed is the Python airtable library; update to install current version given the likelihood of infrequent updates and the very simple code base

