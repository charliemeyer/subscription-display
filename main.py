import os
import urllib
import webapp2
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2

import settings

from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator

decorator = OAuth2Decorator(client_id=settings.CLIENT_ID,
                            client_secret=settings.CLIENT_SECRET,
                            scope=settings.SCOPE)

service = build('gmail', 'v1')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

FORM_PAGE = """<html>
  <body>
    <form action="/" method="post">
      <div><textarea name="content" rows="3" cols="60" placeholder = "enter a valid gmail label name"></textarea></div>
      <div><input type="submit" value="Get emails"></div>
    </form>

    <hr>
  </body>
</html>"""

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

def removeNonAscii(s):
    return "".join([x if ord(x) < 128 else '' for x in s])

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class DbTest(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(50)
        template_values = {
            'greetings': greetings
        }
        template = JINJA_ENVIRONMENT.get_template('results.html')
        self.response.write(template.render(template_values))

class APITest(webapp2.RequestHandler):
    def get(self):
        # lmao so secure
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(50)
        to_write = greetings[0];
        response = {}
        response['lmao'] = to_write.content
        self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

class MainPage(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        self.response.write(FORM_PAGE)

    @decorator.oauth_required
    def post(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        label_name = self.request.get('content')
        labels_response = service.users().labels().list(userId='me').execute(http=decorator.http())
        labels = labels_response['labels']
        label = [""]
        for l in labels:
            if l['name'] == label_name:
                label = [l['id']]
        i = 0
        message_id = ''
        messages = service.users().messages().list(userId='me', labelIds=label).execute(http=decorator.http())
        self.response.write('adding the following messages with tag %s to database' % label_name)
        if messages['messages']:
            for m in messages['messages']:
                greeting = Greeting(parent=guestbook_key(guestbook_name))
                self.response.write('<li>getting message%s</li>' % str(i))
                message_id = m['id']
                i+= 1
                message = service.users().messages().get(userId='me', id=message_id).execute(http=decorator.http())
                snippet = removeNonAscii(message['snippet'])
                greeting.content = snippet
                greeting.put()
                self.response.write('<li>snippet: %s</li>' % snippet)
                self.response.write('<hr>')


class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    (decorator.callback_path, decorator.callback_handler()),
    ('/sign', Guestbook),
    ('/dbtest', DbTest),
    ('/api', APITest),
], debug=True)