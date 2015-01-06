import os
import urllib
import webapp2
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import jinja2
import settings
import logging
import base64
import datetime

# from apiclient.discovery import build
# from oauth2client.appengine import OAuth2Decorator

# decorator = OAuth2Decorator(client_id=settings.CLIENT_ID,
#                             client_secret=settings.CLIENT_SECRET,
#                             scope=settings.SCOPE)

# service = build('gmail', 'v1')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_MESSAGEDB_NAME = 'default_messagedb'

FORM_PAGE = """<html>
  <body>
    <h1>send an email to charles.meyer@tufts.edu if by some mistake you got sent here</h1>
  </body>
</html>"""

def messagedb_key(guestbook_name=DEFAULT_MESSAGEDB_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

def removeNonAscii(s):
    return "".join([x if ord(x) < 128 else '' for x in s])

class Message(ndb.Model):
    """Models an individual Message entry."""
    subject = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class APITest(webapp2.RequestHandler):
    def get(self):
        # lmao so secure
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'
        messagedb_name = DEFAULT_MESSAGEDB_NAME
        messages_query = Message.query(
            ancestor=messagedb_key(messagedb_name)).order(Message.date)
        messages = messages_query.fetch(1)
        response = {}
        response['messages'] = []
        tmpmessage = []
        for i in range(len(messages)):
            if messages[i].subject is None:
                response['subject'] = "Pembroke Schools Update"
            else:
                tmpmessage['subject'] = messages[i].subject
            tmpmessage['body'] = 'lmao' #todo: plz fix, charlie
            response['messages'].push(tmpmessage) 
            
        self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

class MainPage(webapp2.RequestHandler):
    # @decorator.oauth_required
    def get(self):
        self.response.write(FORM_PAGE)

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

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        messagedb_name = DEFAULT_MESSAGEDB_NAME
        message = Message(parent=messagedb_key(messagedb_name))
        html_bodies = mail_message.bodies('text/html')
        # for content_type, body in html_bodies:
        #     message.content += body.decode()
        message.content = 'ayy lmao internet content'
        message.subject = mail_message.subject
        message.put()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    #(decorator.callback_path, decorator.callback_handler()),
    LogSenderHandler.mapping(),
    ('/api', APITest),
], debug=True)
