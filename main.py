import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class User(ndb.Model):
    name = ndb.StringProperty()

    @staticmethod
    def get():
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            user_object = User.query(User.name==nickname).get()
            if not user_object:
                new_user = User(name=nickname)
                new_user.put()
        return user

    def url(self):
        return '/my_writings?key=' + self.key.urlsafe()

class Prompt(ndb.Model):
    text = ndb.StringProperty()
    title = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    def url(self):
        return '/past_writings?key=' + self.key.urlsafe()

class Writing(ndb.Model):
    title = ndb.StringProperty()
    text = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty(kind=User)
    prompt_key = ndb.KeyProperty(kind=Prompt)

    def url(self):
        return '/writing?key=' + self.key.urlsafe()
        #Returns the prompt's url to home with the prompt key
        # must incorporate both user and prompt keys and be accessible through my_writings and past_writings

class Comment(ndb.Model):
    name = ndb.StringProperty()
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
            User.get()
            self.redirect('/home')
        else:
            login_url = users.create_login_url('/user')
            User.get()
            self.redirect(login_url)

#After login
class HomeHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        prompt = Prompt.query().order(-Prompt.date).get()
        template_value = {'logout_url':logout_url,"prompt":prompt}
        template = jinja_environment.get_template("home.html")
        self.response.write(template.render(template_value))

class CreateHandler(webapp2.RequestHandler):
    def get(self):
        prompt = Prompt.query().order(-Prompt.date).get()
        template_value = {"promptTitle":prompt.title, "promptText":prompt.text}
        template = jinja_environment.get_template("create.html")
        self.response.write(template.render(template_value))

    def post(self):
        title = self.request.get('title')
        if title == "":
            title = "[No Title]"

        text = self.request.get('text')

        prompt = Prompt.query().order(-Prompt.date).get()

        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()

        new_writing = Writing(text=text, title=title, prompt_key=prompt.key, user_key=current_user.key) #also need user key
        new_writing.put()
        self.redirect('/past_prompts')

class PastPromptHandler(webapp2.RequestHandler):
    def get(self):
        prompts = Prompt.query().order(-Prompt.date).fetch()
        template_values = {'prompts':prompts}
        template = jinja_environment.get_template("past_prompts.html")
        self.response.write(template.render(template_values))

class PastWritingsHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        prompt = key.get()
        writings = Writing.query(Writing.prompt_key == key).order(-Writing.date).fetch()
        template_values = {'writings':writings, 'prompt':prompt}
        template = jinja_environment.get_template("past_writings.html")
        self.response.write(template.render(template_values))

class MyWritingsHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()
        writings = Writing.query(Writing.user_key == current_user.key).order(-Writing.date).fetch()
        template_values = {'writings':writings}
        template = jinja_environment.get_template("my_writings.html")
        self.response.write(template.render(template_values))

class WritingHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        writing = key.get()
        comments = Comment.query(Comment.writing_key == key).order(Comment.date).fetch()
        template_values = {'writing':writing, 'comments':comments}
        template = jinja_environment.get_template("writing.html")
        self.response.write(template.render(template_values))

    def post(self):
        text = self.request.get('comment')
        writing_key_urlsafe = self.request.get('key')
        writing_key = ndb.Key(urlsafe=writing_key_urlsafe)
        writing = writing_key.get()
        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()
        comment = Comment(text=text, name=current_user.name, writing_key=writing.key) #change from anonymous to user name
        comment.put()
        self.redirect(writing.url())

class AdminHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("admin.html")
        self.response.write(template.render())

    def post(self):
        text = self.request.get('text')
        title = self.request.get('title')
        new_prompt = Prompt(title=title, text=text)
        new_prompt.put()
        self.redirect('/adminCSSI16secrets')

app = webapp2.WSGIApplication([
    ('/', MainHandler),    #Opening Page
    ('/user', UserHandler),
    ('/home', HomeHandler),     #After Login
    ('/past_prompts', PastPromptHandler),
    ('/create', CreateHandler),
    ('/past_writings', PastWritingsHandler),
    ('/my_writings', MyWritingsHandler),
    ('/writing', WritingHandler),
    ('/adminCSSI16secrets', AdminHandler)
], debug=True)
