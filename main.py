import os
import urllib
import webapp2
import json
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import settings
import logging
import base64
import datetime

DEFAULT_MESSAGEDB_NAME = 'pembroke_messagedb'
ACCEPTED_INBOUND_ADDRESS = 'Charie Meyer <cmey63@gmail.com>'
FILTER_NEWLINES = True
TIME_KEY = 'DEFAULT_TIME_KEY'
USE_HTML = True

# returns a datastore key for a given message
def messagedb_key(messagedb_name=DEFAULT_MESSAGEDB_NAME):
    return ndb.Key('Message', messagedb_name)

# stores when requests were last received (for determining which ones are new)
class TimeStamp(ndb.Model):
    time_stored = ndb.DateTimeProperty()
    name = ndb.StringProperty(default=TIME_KEY)
    def update(self):
        self.time_stored = datetime.datetime.now()
        self.put()

# data for each message. time is the time when the message was receieved/stored
class Message(ndb.Model):
    subject = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty()
    time = ndb.DateTimeProperty()

# returns the new messages that have arrived in JSON since the last request
class API(webapp2.RequestHandler):
    def get(self):
        # enable requests from any domain
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'
        messagedb_name = DEFAULT_MESSAGEDB_NAME
        last_time = TimeStamp.query(TimeStamp.name == TIME_KEY).fetch(1)
        if len(last_time) == 0: # if there was no "last request", make a new timestamp
            last_time = TimeStamp()
            last_time.update()
            logging.info('making new timestamp')
        else:
            last_time = last_time[0]
            logging.info('last request made at' + str(last_time.time_stored))
        messages = Message.query(Message.time > last_time.time_stored, ancestor=messagedb_key(messagedb_name)).fetch(100)
        response = {}
        response['messages'] = []
        num_new = len(messages)
        response['num_new'] = num_new     
        for i in range(num_new):
            content = messages[i].content
            if FILTER_NEWLINES:
                content = content.replace('\n', " ")
            content = content.replace('\r', "")
            if messages[i].subject is None: #if there was no subject, give this default
                response['messages'].append({'subject': "Pembroke Schools Update", 'body':content})
            else:
                response['messages'].append({'subject': messages[i].subject, 'body':content})
        self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))
        last_time.update()
        logging.info('this request made at' + str(last_time.time_stored))

# takes incoming mail, parses it and stores it in the database
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
        message.time = datetime.datetime.now()
        logging.info('this message stored @ ' + str(message.time))
        message.put()

app = webapp2.WSGIApplication([
    LogSenderHandler.mapping(),
    ('/api', API),
], debug=True)
