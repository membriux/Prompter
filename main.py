import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

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

# WHENEVER YOU HAVE A HANDLER
# 1. Get info from the request
# 2. Logic -- interact with the database
# 3. Render a response

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
            username = user.nickname()
            self.redirect('/home')
        else:
            login_url = users.create_login_url('/home')
            self.redirect('/' + login_url)

#After login
class HomeHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        template_value = {'logout_url':logout_url}
        template = jinja_environment.get_template("home.html")
        self.response.write(template.render(template_value))

class PastPromptHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("past_prompts.html")
        self.response.write(template.render())

class CreateHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("create.html")
        self.response.write(template.render())

class PastWritingsHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("past_writings.html")
        self.response.write(template.render())

class MyWritingsHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("my_writings.html")
        self.response.write(template.render())

class WritingHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("writings.html")
        self.response.write(template.render())

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
