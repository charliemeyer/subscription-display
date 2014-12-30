#!/usr/bin/python

import httplib2
import sys
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools

def removeNonAscii(s):
    return "".join([x if ord(x) < 128 else '' for x in s])

def get_messages(label):
    i = 0
    messages = gmail_service.users().messages().list(userId='me', labelIds=label).execute()
    if messages['messages']:
        for m in messages['messages']:
            print "getting message " + str(i)
            id = m['id']
            i+= 1
            message = gmail_service.users().messages().get(userId='me', id=id).execute()
            print 'snippet: %s' % removeNonAscii(message['snippet'])

def get_mail(label_name):
    for l in labels:
        # print "id " + l['id']
        # print "name " + l['name']
        if l['name'] == label_name:
            get_messages([l['id']])

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'client_secret_388038159163-1lsfdmjo6d2gscar541kqce2595p73aj.apps.googleusercontent.com.json'
# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
# Location of the credentials storage file
STORAGE = Storage('gmail.storage')
# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()
flags = tools.argparser.parse_args(args=[])
# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, STORAGE, flags, http=http)
# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)
# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)
labels_response = gmail_service.users().labels().list(userId='me').execute()
labels = labels_response['labels']
get_mail(sys.argv[1])

