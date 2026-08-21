# Checkins 3.0 Notes

- Consider transition to a simpler and more robust front-end for tap only
	- With its own micro to handle the card reader input
	- API person lookup
	- Then tap-recording or error-recording via an API call; could be to webhook for Airtable or other simple API endpoint as long as auth is not needed or basic
	- Network connection via POE or WiFi
	- Configured for MITnet when we hand them out
	- Report errors and MACs via RS232
	- API endpoints and auth needs to be programmed by us before handing out
	- BLUE - Ready to tap
	- GREEN - Tap and lookup OK
	- RED - Error on lookup
	- RED FLASHING - No network
	- Physical switch to Eth vs WiFi for network
	- Could power via POE injector for WiFi only setups

- No question on checkin but Airtable could email a one-click survey on checkin, with an opt-out for individuals who don't want to play ball
