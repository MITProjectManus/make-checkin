#!/usr/bin/env python

import sys
import requests
import json
import logging
import time
import argparse
import struct
from secrets import secrets, site, question, logs
import tkinter as tk
from datetime import datetime
from pyairtable import Api
from pyairtable.formulas import match

# Setup command line parser
use_hid = False
parser = argparse.ArgumentParser(description='Card-tap checkin kiosk.')
parser.add_argument('-H',help='use HID Omnikey reader',dest='use_hid',action='store_true')
args = parser.parse_args()
use_hid = args.use_hid

# Setup link to Airtable.  Better way to define base and table?
api_key = secrets['airtable_pat']
api = Api(api_key)
sessions_table = api.table('appFhdhKmHkXVmAlE','tblEqGLp1P9krioA5')
makers_table = api.table('appFhdhKmHkXVmAlE','tblPyVSF6CHM4OY3O')
makerspace_table = api.table('appFhdhKmHkXVmAlE','tblXLR9oHwbhsne1p')

# setup People API info
people_client_id = secrets['people_client_id']
people_client_secret = secrets['people_client_secret']
headers = {'Accept': 'application/json', 'client_id': people_client_id, 'client_secret': people_client_secret}
people_endpoint = 'https://mit-people-v3.cloudhub.io/people/v3/people/'
card_endpoint = 'https://global.api.mit.edu/scanned-id/v1/scanned-ids'

# Some other misc setup
time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
kerb_id = ""
an = "na"

# setup logging
logfile = logs['logfile']
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename=logfile, level=logging.DEBUG)

logging.debug('use HID is %s', use_hid)
#
# A function to convert taps from the HID OMNIKEY to the Cypress Wedge format
#
def hid_to_api(id):
	if len(id)== 11:
		t1 = bin(int(id[len(id) - 7:])).lstrip('0b').rjust(20,'0')+'0'
		t2 = '00110001000110'+t1
		t3 = hex(int(t2,2)).upper().lstrip('0X')
		return(t3)
	else:
		t1 = hex(struct.unpack('<I',struct.pack('>I',int(id)))[0])
		t2 = t1.lstrip('0x').upper()
		return(t2)


# Get site info
site_title = site['title']
site_name = site['name']
site_description = site['description']
site_color_1 = site['color-1']
site_color_2 = site['color-2']
# Get makerspaceID
logging.debug('fetch makerspace ID')
formula = match({'Name':site_name})
result = makerspace_table.all(formula=formula)
makerspace_id = result[0]['id']
logging.debug('received makerspace ID %s', makerspace_id)

def get_new_token():
	logging.captureWarnings(True)
	auth_server_url = "https://mitprod.okta.com/oauth2/aus6sh93rjqnQuszg697/v1/token"
	card_client_id = secrets['card_client_id']
	card_client_secret = secrets['card_client_secret']
	token_req_payload = {'grant_type': 'client_credentials', 'scope' :
	'mit:system:profile.read-by-card'}
	logging.debug('fetch card API access token')
	token_response = requests.post(auth_server_url,
	data=token_req_payload, verify=False, allow_redirects=False,
	auth=(card_client_id, card_client_secret))
			 
	if token_response.status_code !=200:
				logging.debug("Failed to obtain token from the OAuth 2.0 server %s", file=sys.stderr)
				sys.exit(1)
	logging.debug("Successfuly obtained a new token")
	tokens = json.loads(token_response.text)
	return tokens['access_token']

#token = get_new_token()
#card_headers = {'Authorization' : 'Bearer {}'.format(token)}

# Create a window
window = tk.Tk()
window.title(site_title)
window.geometry('480x800')  # Raspberry Pi Display, portrait mode
#window.attributes('-fullscreen',1)  # Fullscreen, no toolbar

# Retrieve Kerberos ID for an given card ID
def card_to_kerb(card_id):
	query = {'id' : card_id}
	token = get_new_token()
	card_headers = {'Authorization' : 'Bearer {}'.format(token)}
	logging.debug('fetch Kerberos ID for card %s', card_id)
	response = requests.post(card_endpoint, json = query, headers = card_headers)
	if response.status_code != 200:
		logging.debug('Invalid ID. Response code: %s',response.status_code)
		return('INVALID_ID')
	else:
		res = json.loads(response.text)
#		print('Name:\t\t{} {}'.format(res['firstName'],res['lastName']))
		logging.debug('Kerberos ID:%s',res['krbName'])
#		print('MIT ID:\t\t{}'.format(res['mitid']))
		return(res['krbName'].lower())

def user_checked_in(user):
	logging.debug('Is %s checked in?',user)
	formula = match({'Kerberos Name':user,'Checked Out':'','Makerspace':site_name})
	result = sessions_table.all(formula=formula)
	if result == []:
		logging.debug('%s not checked in',user)
		return(False)
	else:
		logging.debug('%s is checked in',user)
		return(True)

def check_in(user,answer):
	frm_screen_4.pack_forget()
	frm_notify.pack(pady=(200,0))
	notify_message.config(text = 'One moment...')
	window.update_idletasks()
	window.update()
	logging.debug('check in user %s answer %s',user,answer)
	# Get makerID
	logging.debug('get makerID for user %s',user)
	formula = match({'Kerberos Name':user})
	result = makers_table.all(formula=formula)
	maker_id = result[0]['id']
	logging.debug('makerID %s received',maker_id)
	update = {}
	update['Maker'] = [maker_id]
	update['Makerspace'] = [makerspace_id]
	update['Survey Response'] = answer
	logging.debug('updating sessions table with %s',update)
	sessions_table.create(update)
	logging.debug('sessions table updated')
	notify_message.config(text = 'You\'re checked in!')
	window.update_idletasks()
	window.update()
	time.sleep(3)
	
def check_out(user):
	frm_screen_1.pack_forget()
	frm_notify.pack(pady=(200,0))
	notify_message.config(text = 'One moment...')
	window.update_idletasks()
	window.update()
	logging.debug('check out user %s',user)
	timestamp = datetime.utcnow()
	logging.debug('get sessionID for user %s',user)
	formula = match({'Kerberos Name':user,'Checked Out':'','Makerspace':site_name})
	result = sessions_table.all(formula=formula)
	session_id = result[0]['id']
	logging.debug('sessionID %s received',session_id)
	update = {}
	update['Checked Out'] = timestamp.strftime(time_format)
	logging.debug('updating sessions table with %s',update)
	sessions_table.update(session_id,update)
	logging.debug('sessions table updated')
	notify_message.config(text = 'You\'re checked out!\nHave a good day!')
	window.update_idletasks()
	window.update()
	time.sleep(3)


# Process a card tap
def handle_card_tap(event):
	global kerb_id
	global an
	# Put up a 'One moment...' screen
	frm_screen_1.pack_forget()
	frm_notify.pack(pady=(200,0))
	notify_message.config(text = 'One moment...')
	window.update_idletasks()
	window.update()
	an = 'na'
	tmp_id = entry_tap.get().lower()
	if (not use_hid):
		card_id = tmp_id.split('=')[1]
	else:
		card_id = hid_to_api(tmp_id)
	logging.debug('processing card tap %s',card_id)
	kerb_id = card_to_kerb(card_id)
	if (kerb_id == 'INVALID_ID' or kerb_id == None): # restart if invalid card or Kerberos ID
		logging.debug("Invalid ID")
		frm_notify.pack_forget()
		frm_invalid_id.pack(pady=(200,0))
		window.update_idletasks()
		window.update()
		time.sleep(5)
		frm_invalid_id.pack_forget()
		frm_screen_1.pack(pady=(200,0))
		window.update_idletasks()
		window.update()
	else:
		# Is user a maker in Airtable?
		email = kerb_id + '@mit.edu'
		logging.debug('Is %s a maker',email)
		formula = match({'Email':email})
		result = makers_table.all(formula=formula)
		if result == []:
			# user is not a maker in Airtable so add them
			logging.debug('%s is not an active maker, adding them.',email)
			update = {}
			update['Email'] = email
			makers_table.create(update)
			logging.debug('%s added',email)
		else:
			logging.debug('%s is an active maker.',email)
		if (not user_checked_in(kerb_id)):
			frm_notify.pack_forget()
			frm_screen_4.pack(pady=(120,0))
			window.update_idletasks()
			window.update()
			start = time.monotonic()
			while time.monotonic()-start < 10:
				window.update_idletasks()
				window.update()
# If question times out, process here
			if an == 'na':
				print('Checkin ',kerb_id,'\tna')
				check_in(kerb_id,'na')
			frm_notify.pack_forget()
			frm_screen_1.pack(pady=(200,0))
			window.update_idletasks()
			window.update()
		else:
			print('Checkout ',kerb_id)
			check_out(kerb_id)
			frm_notify.pack_forget()
			frm_screen_1.pack(pady=(200,0))
			window.update_idletasks()
			window.update()

	entry_tap.delete(0,tk.END)
	entry_tap.focus_set()
	window.update_idletasks()
	window.update()

def handle_answer(ans):
# If question is answered process here
	global an
	an = ans.lower()
	print('Checkin ',kerb_id,'\t',an)
	check_in(kerb_id,an)
	frm_notify.pack_forget()
	frm_screen_1.pack(pady=(200,0))
	entry_tap.delete(0,tk.END)
	entry_tap.focus_set()
	window.update_idletasks()
	window.update()


# Define frame for first screen
frm_screen_1 = tk.Frame(master=window)
frm_screen_1.pack(pady=(200,0))
frm_screen_1.columnconfigure([0], minsize='460')
frm_screen_1.rowconfigure([0,1,2,3,4,5,6,7], minsize='75')
title_1 = tk.Label(master=frm_screen_1,text = 'Welcome to '+site_title,font = ('Arial',25), bg=site_color_1)
title_1.grid(column=0, row=0, sticky='ew', columnspan=2)
title_2 = tk.Label(master=frm_screen_1,text = site_description,font = ('Arial',20))
title_2.grid(column=0,row=1,sticky='ew',columnspan=2,pady=20)
title_3 = tk.Label(master=frm_screen_1,text = 'Tap your MIT ID to proceed',font = ('Arial',20))
title_3.grid(column=0,row=2,sticky='ew',columnspan=2,pady=20)
entry_tap = tk.Entry(master=frm_screen_1,font = ('Arial',25),show='*')
entry_tap.grid(column=0,row=6,sticky='ew',padx=50)
entry_tap.focus_set()

# Define frame for invalid ID notification
frm_invalid_id = tk.Frame(master=window)
frm_invalid_id.columnconfigure([0], minsize='460')
frm_invalid_id.rowconfigure([0,1,2,3,4,5,6,7], minsize='75')
invalid_id_message = tk.Label(master=frm_invalid_id,text = 'Invalid ID',font = ('Arial',25))
invalid_id_message.grid(column=0, row=0, sticky='ew', columnspan=2)

# Define frame for question screen
ab = []
frm_screen_4 = tk.Frame(master=window)
frm_screen_4.rowconfigure([0,1,2,3,4,5,6,7,8,9,10], minsize=15)
frm_screen_4.columnconfigure([0],minsize='460')
prompt_question = tk.Label(master=frm_screen_4,text = question['question'],font = ('Arial',20))
for i,a in enumerate(question['answers']):
	ab.append(tk.Button(master=frm_screen_4,height = 2,text = question['answers'][i],font=('Arial',15),command = lambda t = question['answers'][i] : handle_answer(t)))
prompt_question.grid(column=0,row=0,sticky='ew')
for i,j in enumerate(ab):
	j.grid(column=0,row=i+1,sticky='ew')
reset_question = tk.Button(master=frm_screen_4,text = 'RESTART',font = ('Arial',20), height = 2)
reset_question.grid(column=0,row=i+5,sticky='ew')

# Define frame for notifications
frm_notify = tk.Frame(master=window)
frm_notify.columnconfigure([0], minsize='460')
frm_notify.rowconfigure([0,1,2,3,4,5,6,7], minsize='75')
notify_message = tk.Label(master=frm_notify,font=('Arial',25))
notify_message.grid(column=0, row=0, sticky='ew', columnspan=2)

entry_tap.bind('<Return>',handle_card_tap)

window.mainloop()