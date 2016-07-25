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

class Writing(ndb.Model):
    title = ndb.StringProperty()
    text = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty(kind=User)
    prompt_key = ndb.KeyProperty(kind=Prompt)

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
        # 1. Get info from the request
        # 2. Logic -- interact with the database
        # 3. Render a response
        template = jinja_environment.get_template(_____)
        self.response.write(template.render())

class UserHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template(‘User.html')
        self.response.write(template.render())
        # 1. Get info from the request
        # 2. Logic -- interact with the database
        # 3. Render a response
        user = users.get_current_user()

app = webapp2.WSGIApplication([
    ('/', MainHandler),    #Opening Page
    ('/user', UserHandler),    #Get the User info
    ('/home', HomeHandler)     #After Login
], debug=True)
