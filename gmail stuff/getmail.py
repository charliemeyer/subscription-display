#!/usr/bin/python

import httplib2
import sys
import base64
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
            message = gmail_service.users().messages().get(userId='me', id=id, format='raw').execute()
            print 'snippet: %s' % removeNonAscii(message['snippet'])
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            print msg_str
            print "________________________________________________"
            # if message['payload']['parts']:
            #     for part in message['payload']['parts']:
            #         print 'mimrtype: %s' % part

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



    # @decorator.oauth_required
    # def post(self):
    #     guestbook_name = self.request.get('guestbook_name',
    #                                       DEFAULT_MESSAGEDB_NAME)
    #     label_name = self.request.get('content')
    #     labels_response = service.users().labels().list(userId='me').execute(http=decorator.http())
    #     labels = labels_response['labels']
    #     label = [""]
    #     for l in labels:
    #         if l['name'] == label_name:
    #             label = [l['id']]
    #     i = 0
    #     message_id = ''
    #     messages = service.users().messages().list(userId='me', labelIds=label).execute(http=decorator.http())
    #     self.response.write('adding the following messages with tag %s to database' % label_name)
    #     if messages['messages']:
    #         for m in messages['messages']:
    #             message = message(parent=guestbook_key(guestbook_name))
    #             self.response.write('<li>getting message%s</li>' % str(i))
    #             message_id = m['id']
    #             i+= 1
    #             message = service.users().messages().get(userId='me', id=message_id).execute(http=decorator.http())
    #             snippet = removeNonAscii(message['snippet'])
    #             message.content = snippet
    #             message.put()
    #             self.response.write('<li>snippet: %s</li>' % snippet)
    #             self.response.write('<hr>')
