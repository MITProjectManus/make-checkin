#
# Example location configuration file. The production file
# needs to be named "config.py" and managed locally for 
# each kiosk deployment. It will contain API keys and is
# not tracked in the repository. You can use this example
# file for reference in creating your local "config.py".
#

secrets = {
    'airtable_pat' : '',         # Making at MIT Airtable Base PAT
    'people_client_id' : '',     # MIT People API Client ID
    'people_client_secret' : '', # MIT People API Client Secret
    'card_client_id' : '',       # MIT Card API Client ID
    'card_client_secret' : ''    # MIT Card API Client Secret
}

site = {
    'title' : 'Makerspace',                   # Name as shown on checkin screen
    'name' : 'Makerspace',                    # Name as used in Airtable
    'description' : 'Makerspace Description', # Description shown on checkin screen
    'color-1' : '#57b99d',                    # Makerspace theme color
    'color-2' : '#3d816e'                     # Makerspace theme color, dark
}

question = {
    'question' : 'What brings you to {} today?'.format(site['title']),
    'answers' : ['PERSONAL','RESEARCH','TRAINING','ENTREPRENEURSHIP','ON DUTY','CLUBS AND TEAMS','OTHER'],
    'freeform' : '' # Currently not supported as it requires keyboard support
}

logs = {
    'logfile' : ''  # If set will write logging entries to file, logging disabled if blank
}

