# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python Tkinter kiosk application that runs on Raspberry Pi hardware at MIT makerspaces. When a user taps their MIT ID card, the app reads the card data, resolves it to a Kerberos ID via the MIT Card API, then checks them in or out via Airtable.

## Running the app

```bash
# Standard mode (Cypress Wedge HID card reader, outputs keystrokes like a keyboard)
python make-checkin.py

# HID Omnikey reader mode (raw card data, requires byte conversion)
python make-checkin.py -H
```

Install the only non-stdlib dependency first:

```bash
pip install pyairtable
```

## Configuration

`config.py` is not tracked (excluded via `.gitignore`). Copy `config-example.py` to `config.py` and fill in:

- `secrets`: Airtable PAT, MIT People API credentials, MIT Card API credentials
- `site`: Display name, Airtable name, description, theme colors
- `question`: The check-in survey question and answer choices
- `logs`: Path to log file (empty string disables file logging)

The `config.py` file is imported as `from secrets import secrets, site, question, logs` — the module name `secrets` in `config.py` shadows Python's stdlib `secrets` module.

## Architecture

The entire application is a single file (`make-checkin.py`) with no class structure. Execution flow:

1. **Startup**: Connects to Airtable, fetches the makerspace record ID by name, builds the Tkinter window.
2. **Card tap** (`handle_card_tap`): Triggered by `<Return>` on a hidden `Entry` widget that stays focused — the card reader acts as a keyboard and types the card data followed by Enter.
3. **Card resolution**: `card_to_kerb()` calls the MIT Card API (OAuth2 client credentials via Okta) to convert raw card ID to a Kerberos username. Each tap fetches a fresh OAuth token.
4. **Check-in/out decision**: `user_checked_in()` queries the Airtable Sessions table for an open session (no checkout timestamp). If none exists, shows the survey question frame; if one exists, calls `check_out()`.
5. **Airtable writes**: `check_in()` creates a new Sessions record linked to the Maker and Makerspace records. `check_out()` updates the existing session record with a checkout timestamp.
6. **Survey timeout**: The question screen runs a busy-wait loop (`time.monotonic`) for 10 seconds calling `window.update()`. If `handle_answer()` sets the global `an` variable before timeout, that answer is used; otherwise `'na'` is recorded.

## Airtable schema (hardcoded IDs)

- Base: `appFhdhKmHkXVmAlE`
- Sessions table: `tblEqGLp1P9krioA5` — fields: `Maker` (linked), `Makerspace` (linked), `Survey Response`, `Checked Out` (datetime)
- Makers table: `tblPyVSF6CHM4OY3O` — fields: `Kerberos Name`, `Email`
- Makerspace table: `tblXLR9oHwbhsne1p` — fields: `Name`

## HID reader conversion (`hid_to_api`)

The `-H` flag enables HID Omnikey reader mode. The raw output format differs from the Cypress Wedge format expected by the MIT Card API, so `hid_to_api()` converts it. Two paths: 11-digit IDs go through a bit-manipulation path; other lengths go through a byte-swap path.

## Raspberry Pi deployment

See `SETUP-RASPBERRY-PI.md` for full hardware/software setup. The kiosk auto-starts via:

- `setup/Raspberry Pi/make-checkin.service` — systemd unit that starts after the graphical target
- `setup/Raspberry Pi/launch-make-checkin.sh` — shell wrapper that sets `DISPLAY=:0`, disables screensaver, and calls the script with `-H`

The display runs in X11 (not Wayland) at 480×800 portrait mode. Fullscreen is commented out in the code (issue #11 in README tracks switching to Wayland fullscreen).
