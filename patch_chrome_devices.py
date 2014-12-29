#!/usr/bin/python

import httplib2
import csv

from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


# Check https://developers.google.com/admin-sdk/directory/v1/guides/authorizing for all available scopes
OAUTH_SCOPE   = 'https://www.googleapis.com/auth/admin.directory.device.chromeos'

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

with open(INPUT_FILE) as f:
  reader = csv.DictReader(f, dialect='excel-tab')
  for row in reader:
    deviceId = row['id']
    assetNumber = row['notes']
    if assetNumber != 'None':
      body = {
        'notes': assetNumber
      }
      print("patching %s with %s" % (deviceId, body['notes']))
      result = directory_service.chromeosdevices().patch(customerId='my_customer', deviceId=deviceId, body=body).execute()
      print("%s" % result)
      break
