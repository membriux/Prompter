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
    title = ndb.StringProperty()

    #def url(self):
        #return '/home?key=' + self.key.urlsafe()
        # Returns the prompt's url to home with the prompt key

class Writing(ndb.Model):
    title = ndb.StringProperty()
    text = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty(kind=User)
    prompt_key = ndb.KeyProperty(kind=Prompt)

    #def urlHome(self):
        #return '/home?key=' + self.key.urlsafe()
        # Returns the prompt's url to home with the prompt key

class Comment(ndb.Model):
    # username from userkey
    date = ndb.DateTimeProperty(auto_now_add=True)
    text = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    writing_key = ndb.KeyProperty(kind=Writing)

#For generic homepage
class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("Main.html")
        self.response.write(template.render())

# Use Google's page, don't make your own
class UserHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
                nickname, logout_url)
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))

#After login
class HomeHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("home.html")
        self.response.write(template.render())

class 

app = webapp2.WSGIApplication([
    ('/', MainHandler),    #Opening Page
    ('/user', UserHandler),
    ('/home', HomeHandler),     #After Login
    ('/past_prompts', PastPromptHandler),
    ('/create', CreateHandler),
    ('/past_writings', PastWritingsHandler),
    ('/my_writings', MyWritingsHandler),
    ('/writing', WritingHandler)
], debug=True)
