#!/bin/bash
#
# Raspberry Pi OS launch script for the GUI application
export DISPLAY=:0
xset s 0
xset -dpms
/home/pi/make-checkin/make-checkin.py -H
