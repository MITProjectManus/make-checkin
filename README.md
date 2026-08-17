# Make: Checkin

A card tap check-in kiosk for MIT makerspaces. Runs on a Raspberry Pi with a touchscreen and a USB HID card reader. Users tap their MIT ID card, the system resolves it to their Kerberos ID via the MIT Card API, and records a check-in or check-out session in Airtable.

This replaces [Airtable-Card-Checkin](https://github.com/MITProjectManus/Airtable-Card-Checkin), the original prototype version of card tap check-in for MIT makerspaces.

## How it works

1. The kiosk shows a welcome screen and waits for a card tap.
2. A card tap is read by the USB HID card reader, which sends card data to the app via simulated keyboard input (ending with Enter).
3. The app calls the MIT Card API to convert the raw card ID to a Kerberos username.
4. If the user has no open session in Airtable, they are shown a brief survey question (e.g., "What brings you here today?") and checked in.
5. If the user already has an open session, they are checked out immediately.
6. All sessions are recorded in Airtable with the linked maker record, makerspace, survey response, and check-out timestamp.

## Hardware and Software Setup

For the complete hardware bill of materials, assembly, OS installation, and software configuration for the standard Raspberry Pi 4 kiosk, see:

**[SETUP-RASPBERRY-PI.md](SETUP-RASPBERRY-PI.md)**

## Configuration

Each kiosk requires a `config.py` file that is **not tracked** in this repository. Create it by copying `config-example.py`:

```bash
cp config-example.py config.py
```

Then fill in the values for your specific kiosk deployment.

### `secrets` — API credentials

| Key | Description |
|-----|-------------|
| `airtable_pat` | Airtable Personal Access Token for the Making at MIT base |
| `people_client_id` | MIT People API Client ID |
| `people_client_secret` | MIT People API Client Secret |
| `card_client_id` | MIT Card API Client ID (OAuth2 client credentials) |
| `card_client_secret` | MIT Card API Client Secret |

### `site` — Location settings

| Key | Description |
|-----|-------------|
| `title` | Makerspace display name shown on the check-in screen |
| `name` | Makerspace name exactly as it appears in Airtable |
| `description` | Short description shown on the check-in screen |
| `color-1` | Primary theme color (hex, e.g. `#57b99d`) |
| `color-2` | Secondary/dark theme color (hex) |

The `name` field must match the makerspace record name in Airtable exactly — it is used to look up the Airtable record ID at startup.

### `question` — Check-in survey

| Key | Description |
|-----|-------------|
| `question` | Survey question shown at check-in |
| `answers` | List of answer button labels shown to the user |

The survey appears after a card tap for a new check-in and times out after 10 seconds, recording `'na'` if no answer is selected.

### `logs`

| Key | Description |
|-----|-------------|
| `logfile` | Absolute path to log file; leave empty string to disable file logging |

## Running

Install the one required dependency:

```bash
pip install --break-system-packages -r requirements.txt
```

Run the app:

```bash
# Cypress Wedge card reader (outputs keystrokes like a keyboard)
python make-checkin.py

# HID Omnikey card reader (raw binary card data — standard deployed configuration)
python make-checkin.py -H
```

On a deployed kiosk the app is launched automatically via a systemd service and restarts automatically if it exits. See [SETUP-RASPBERRY-PI.md](SETUP-RASPBERRY-PI.md) for full details.

## Known Issues and Needed Enhancements

1. Sometimes stuck on "One moment..." screen — possibly triggered by invalid card data or a momentary network loss
2. Ignoring the follow-up survey question will block the kiosk until someone selects an answer; it should time out and complete the check-in with `'na'`
3. Better error handling, health monitoring, and recovery — most errors and blocking states are silent or only logged in the background; consider a watchdog timer for automatic restart
4. Network status and API reachability are not surfaced to the user; should show an indicator if offline and retry connections periodically
5. A failure response from the MIT Card API should be shown to the user, including the card token that was read and the API error code
6. Performance is slow — likely improvable with more compact API calls, fewer open-ended Airtable searches, and local caching of maker records
7. Only MIT IDs are supported currently; should fall back to a registered MiFare tap ID in Airtable when MIT ID lookup fails
8. Input buffer may not be cleared before reading the next card tap
9. Better idle screen and button graphics
10. Consider switching to landscape orientation; portrait mode requires display rotation configuration with no functional advantage
11. Fullscreen mode currently requires X11 — update to support fullscreen under Wayland to simplify OS configuration
12. Investigate whether there is a touch input event library available for Tkinter
13. Consider switching to [guizero](https://lawsie.github.io/guizero/) (a simplified wrapper over Tkinter) for easier maintenance
