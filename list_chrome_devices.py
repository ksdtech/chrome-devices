#!/usr/bin/python

import httplib2

from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


# Check https://developers.google.com/admin-sdk/directory/v1/guides/authorizing for all available scopes
OAUTH_SCOPE   = 'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly'

# Copy your credentials and redirect URI from the Google developers console 
# "Client ID for native application" and put them into client_secrets.py
# module:

# CLIENT_ID     = 'my_client_id'
# CLIENT_SECRET = 'my_client_secret'
# REDIRECT_URI  = 'urn:ietf:wg:oauth:2.0:oob'
# OUTPUT_FILE   = 'path/to/output.txt'

from client_secrets import *

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

directory_service = build('admin', 'directory_v1', http=http)

# see https://developers.google.com/admin-sdk/directory/v1/reference/chromeosdevices
all_devices = []
page_token = None
params = {'customerId': 'my_customer'}

while True:
  try:
    if page_token:
      params['pageToken'] = page_token
    current_page = directory_service.chromeosdevices().list(**params).execute()

    all_devices.extend(current_page['chromeosdevices'])
    page_token = current_page.get('nextPageToken')
    if not page_token:
      break
  except errors.HttpError as error:
    print 'An error occurred: %s' % error
    break
    

with open(OUTPUT_FILE, 'w') as f:
  f.write("id\tserial\tmac\tmodel\tstatus\tnotes\tos\tfirmware\tenrolled\tsynced\n")
  for device in all_devices:
    mac = device.get('macAddress')
    if mac is not None:
      mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12] 
    f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
      device.get('deviceId'),
      device.get('serialNumber'), mac, 
      device.get('model'), device.get('status'), device.get('notes'),
      device.get('osVersion'), device.get('firmwareVersion'), 
      device.get('lastEnrollmentTime'), device.get('lastSync')))
