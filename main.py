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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_MESSAGEDB_NAME = 'pembroke_messagedb'
ACCEPTED_INBOUND_ADDRESS = 'Charie Meyer <cmey63@gmail.com>'
FILTER_NEWLINES = True
TIME_KEY = 'LMAO'

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

class TimeStamp(ndb.Model):
    time_stored = ndb.DateTimeProperty()
    key = ndb.StringProperty(TIME_KEY)
    def update(self):
        self.time_stored = datetime.datetime.now()
        self.put()

class Message(ndb.Model):
    """Models an individual Message entry."""
    subject = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class APITest(webapp2.RequestHandler):
    def get(self):
        # lmao so secure
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'
        messagedb_name = DEFAULT_MESSAGEDB_NAME
        last_time = TimeStamp.query(key == TIME_KEY).fetch(1)
        messages = Message.query(ancestor=messagedb_key(messagedb_name), Message.date > last_time).fetch(100)
        response = {}
        response['messages'] = []
        num_new = len(messages)
        response['num_new'] = num_new     
        for i in range(num_new):
            content = messages[i].content
            if FILTER_NEWLINES:
                content = content.replace('\n', " ")
            content = content.replace('\r', "")
            if messages[i].subject is None:
                response['messages'].append({'subject': "Pembroke Schools Update", 'body':content})
            else:
                response['messages'].append({'subject': messages[i].subject, 'body':content})
        self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))
        last_time.update()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(FORM_PAGE)

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        if mail_message.sender != ACCEPTED_INBOUND_ADDRESS:
            logging.info("Message from unknown sender, ignoring")
        messagedb_name = DEFAULT_MESSAGEDB_NAME
        message = Message(parent=messagedb_key(messagedb_name))
        plain_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')
        message.content = ""
        if USE_HTML:
            for content_type, body in html_bodies:
                message.content += body.decode()
        else:
            for content_type, body in plain_bodies:
                message.content += body.decode()
        if mail_message.subject is None:
            message.subject = "Pembroke Schools Update"
        else:
            message.subject = mail_message.subject
        message.put()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    LogSenderHandler.mapping(),
    ('/api', APITest),
], debug=True)
