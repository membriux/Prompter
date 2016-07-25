import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# WHENEVER YOU HAVE A HANDLER
# 1. Get info from the request
# 2. Logic -- interact with the database
# 3. Render a response

class User(ndb.Model):
    email = ndb.StringProperty()
    name = ndb.StringProperty()

class Prompt(ndb.Model):
    text = ndb.StringProperty()

    def url(self):
        return '/home?key=' + self.key.urlsafe()

class Writing(ndb.Model):
    title = ndb.StringProperty()
    text = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty(kind=User)
    prompt_key = ndb.KeyProperty(kind=Prompt)

    def urlHome(self):
        return '/home?key=' + self.key.urlsafe()

class Comment(ndb.Model):
    # name from userkey
    date = ndb.DateTimeProperty(auto_now_add=True)
    text = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    writing_key = ndb.KeyProperty(kind=Writing)

#For generic homepage
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # 1. Get info from the request
        # 2. Logic -- interact with the database
        # 3. Render a response
        template = jinja_environment.get_template('Main.html')
        self.response.write(template.render())
        user = users.get_current_user()

#After login
class HomeHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        prompt = key.get()
        writings = Writing.query(Writing.prompt_key == key).order(-Writing.date).fetch()
        template_values = {'writings':writings}
        template = jinja_environment.get_template("home.html")
        self.response.write(template.render(template_values))

    def post(self):
        #1. get info from Request
        title = self.request.get('title')
        text = self.request.get('text')
        #2. logic (interact with database)
        new_writing = Writing(text=text, title=title)
        new_writing.put()
        #3. render response
        self.redirect('/')

# Use Google's page, don't make your own
class UserHandler(webapp2.RequestHandler):
    def get(self):
        # 1. Get info from the request
        user = users.get_current_user()
        # 2. Logic -- interact with the database
        user_values = {}
        if user:
            username = user.nickname()
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
                username, logout_url)
            user_values = {'username':username}
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))
        template = jinja_environment.get_template('Main.html')
        #self.response.write(template.render(user_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler),    #Opening Page
    ('/user'), UserHandler),
    ('/home', HomeHandler)     #After Login
], debug=True)
