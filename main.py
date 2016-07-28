import webapp2
import jinja2
import os
import logging
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
        return '/user_writings?key=' + self.key.urlsafe()

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
    count = ndb.IntegerProperty()
    user_votes = ndb.KeyProperty(kind=User, repeated=True)

    def url(self):
        return '/writing?key=' + self.key.urlsafe()
        #Returns the prompt's url to home with the prompt key
        # must incorporate both user and prompt keys and be accessible through my_writings and past_writings

    #method to check if user voted
    def voted(self, user):
        if self.user_votes:
            if user.key in self.user_votes:
                return True
            else:
                return False
        else:
            return False

    #method to see if writing already has votes
    def voteCount(self):
        if self.count == None:
            return 0
        else:
            return self.count

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

        #Filter writing from second to last prompt (second most recent)
        two_prompts = Prompt.query().order(-Prompt.date).fetch(2)
        #Order by date, most recent first
        #Fetch the first two
        featured_prompt = two_prompts[1]
        #Then take the second of the two and get key
        featured_prompt_key = featured_prompt.key

        #take all writings for that prompt
        forPrompt_writings = Writing.query(Writing.prompt_key == featured_prompt_key).order(-Writing.date).fetch()
        special_writings = {}

        #loop and find the count for each writing
        for forPrompt_writing in forPrompt_writings:
            vote_count = forPrompt_writing.count
            #Value of dict: count of votes (int)
            key_of_writing = forPrompt_writing.key
            #Key of dict: writing.key of writing page (key)
            special_writings[key_of_writing] = vote_count

        most_vote = max(special_writings, key=special_writings.get)
        #Find max value from dict and matching writing.key

        featured_story = most_vote.get()
        #Send writing.key to home and add it on featured bubble

        template_value = {'logout_url':logout_url,"prompt":prompt, "featured_story":featured_story}
        template = jinja_environment.get_template("home.html")
        self.response.write(template.render(template_value))

class CreateHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        prompt = Prompt.query().order(-Prompt.date).get()
        template_value = {"promptTitle":prompt.title, "promptText":prompt.text, 'logout_url':logout_url}
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
        logout_url = users.create_logout_url('/')
        prompts = Prompt.query().order(-Prompt.date).fetch()
        template_values = {'prompts':prompts, 'logout_url':logout_url}
        template = jinja_environment.get_template("past_prompts.html")
        self.response.write(template.render(template_values))

class PastWritingsHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        prompt = key.get()
        writings = Writing.query(Writing.prompt_key == key).order(-Writing.date).fetch()
        template_values = {'writings':writings, 'prompt':prompt, 'logout_url':logout_url}
        template = jinja_environment.get_template("past_writings.html")
        self.response.write(template.render(template_values))

class MyWritingsHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()
        writings = Writing.query(Writing.user_key == current_user.key).order(-Writing.date).fetch()
        template_values = {'writings':writings, 'logout_url':logout_url}
        template = jinja_environment.get_template("my_writings.html")
        self.response.write(template.render(template_values))

class WritingHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')

        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()

        writing_key_urlsafe = self.request.get('key')
        writing_key = ndb.Key(urlsafe=writing_key_urlsafe)
        writing = writing_key.get()

        already_voted = writing.voted(current_user)
        check_count = writing.voteCount()
        writing.count = check_count
        writing.put()

        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        writing = key.get()
        comments = Comment.query(Comment.writing_key == key).order(Comment.date).fetch()
        template_values = {'writing':writing, 'comments':comments, 'logout_url':logout_url, "already_voted":already_voted}
        template = jinja_environment.get_template("writing.html")
        self.response.write(template.render(template_values))

    def post(self):
        vote = self.request.get('vote')
        logging.info(vote)

        user = users.get_current_user()
        nickname = user.nickname()
        current_user = User.query(User.name==nickname).get()

        writing_key_urlsafe = self.request.get('key')
        writing_key = ndb.Key(urlsafe=writing_key_urlsafe)
        writing = writing_key.get()

        #if vote button is pressed
        if vote:
            check_vote = writing.voted(current_user)
            if check_vote:
                logging.info("You have already voted!")
            else:
                logging.info("New Vote!")
                writing.user_votes.append(current_user.key)
                logging.info(writing.user_votes)
                writing.count = writing.count + 1
                writing.put()
        #if posting a comment
        else:
            text = self.request.get('comment')
            writing_key_urlsafe = self.request.get('key')
            writing_key = ndb.Key(urlsafe=writing_key_urlsafe)
            writing = writing_key.get()
            comment = Comment(text=text, name=current_user.name, writing_key=writing.key, user_key=current_user.key)
            comment.put()
        self.redirect(writing.url())

class UserPageHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe_key)
        user = key.get()
        #logging.info("You've made it to this page")
        writings = Writing.query(Writing.user_key == key).order(-Writing.date).fetch()
        template_values = {'writings':writings, 'logout_url':logout_url, 'user':user}
        template = jinja_environment.get_template("user_writings.html")
        self.response.write(template.render(template_values))

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

class AboutSiteHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        template = jinja_environment.get_template("about_site.html")
        template_values = {'logout_url':logout_url}
        self.response.write(template.render(template_values))

class AboutDevelopersHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        template = jinja_environment.get_template("about_developers.html")
        template_values = {'logout_url':logout_url}
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler),    #Opening Page
    ('/user', UserHandler),
    ('/home', HomeHandler),     #After Login
    ('/past_prompts', PastPromptHandler),
    ('/create', CreateHandler),
    ('/past_writings', PastWritingsHandler),
    ('/my_writings', MyWritingsHandler),
    ('/writing', WritingHandler),
    ('/adminCSSI16secrets', AdminHandler),
    ('/about_site', AboutSiteHandler),
    ('/about_developers', AboutDevelopersHandler),
    ('/user_writings', UserPageHandler)
], debug=True)
