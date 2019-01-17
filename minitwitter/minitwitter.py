'''
Created on 10.05.2013

@author: Tobias
'''

from server.webserver import Webserver, App, StopProcessing
from server.apps.static import StaticApp
from server.apps.usermanagement import UsermanagementApp
from server.apps.static import StaticApp
from server.middlewares.session import SessionMiddleware
from server.log import log
from server.tweetmodel import Tweets
import server.usermodel

import sqlite3 as sqlite
from urllib.parse import quote, unquote


class MiniTwitterApp(App):
    """Create and display status messages"""

    def __init__(self, datadir='data', db_connection=None):
        self.datadir = datadir
        self.db_connection = db_connection
        super().__init__()

    def register_routes(self):
        self.server.add_route(r"/?$", self.show)
        self.server.add_route(r"/logout$", self.logout)
        self.server.add_route(r"/login$", self.login)

    def show(self, request, response, pathmatch, message=''):
        """Process all requests. Dispatch POST to save method. Show tweets on GET requests."""

        if request.method.lower() == 'post':
            return self.save(request, response, pathmatch)

        try:
            user = request.session['user']
        except (AttributeError, KeyError):
            user = server.usermodel.AnonymousUser()

        d = {'tweets': self.getTweets(), 'message': message, 'user': user }

        response.send_template('minitwitter.tmpl', d)

    def getTweets(self):
        tweets = Tweets(self.db_connection)
        m = []  # list of tweets

        #closed xss lücke mit replace
        for tweet in tweets.findTweets():  # parse all lines and build array of tweets with dates
            m.append({'date': tweet.date, 'tweet': tweet.message.replace('<', '&lt'), 'author': tweet.username})

        if not m:
            m.append({'date': 'No news', 'tweet': 'Create some.', 'author': 'The Minitwitter'})
        m.reverse()

        return m

    def save(self, request, response, pathmatch):
        """Process post request to save new tweet."""

        if 'user' not in request.session:
            raise StopProcessing(400, "You need to be logged in.")

        try:
            status = request.params['status']
        except KeyError:
            raise StopProcessing(500, "No status given.")

        try:
            tweets = Tweets(self.db_connection)
            tweets.createTweet(request.session['user'].fullname, status)
        except IOError:
            raise StopProcessing(500, "Unable to connect to data file.")

        d = {'tweets': self.getTweets(), 'message': 'Great! Now the world knows.', 'user': request.session['user']}
        response.send_template('minitwitter.tmpl', d)

    def logout(self, request, response, pathmatch):
        """Logout user and show a success message."""
        if request.session:
            request.session.destroy()
        self.show(request, response, pathmatch, "Successfully logged out")

    def login(self, request, response, pathmatch):
        """Shoow login form if necessary or check provided credentials."""
        if 'user' in request.session:  # already logged in
            return response.send_redirect("/")
        if '_username' in request.params and '_password' in request.params:
            users = server.usermodel.Users(self.db_connection)
            user = users.login(request.params['_username'], request.params['_password'])
            if user is not None:
                request.session['user'] = user  # save user to session
                d = {'tweets': self.getTweets(), 'message': 'Successfully logged in as <i>' + request.params['_username'] + '</i>',
                     'user': request.session['user']}

                return response.send_template('minitwitter.tmpl', d)
            else:
                return response.send_template('login.tmpl', {'message': 'Wrong username or password. Try again.', 'user': server.usermodel.AnonymousUser()})
        # send login form
        return response.send_template('login.tmpl',{'user': server.usermodel.AnonymousUser()})


if __name__ == '__main__':

    db = sqlite.connect('minitwitter.sqlite')  # use sqlite db
    db.row_factory = sqlite.Row  # fetch rows as Row objects (easier to access)

    s = Webserver()
    s.set_templating("jinja2")
    s.set_templating_path("templates.jinja2")

    s.add_middleware(SessionMiddleware())

    s.add_app(UsermanagementApp(db_connection=db))   # Sub-App: create, change, delete users. (code in server/apps)
    s.add_app(StaticApp(prefix='static', path='static'))  # deliver static files

    s.add_app(MiniTwitterApp('data', db_connection=db))  # the twitter app

    log(0, "Server running.")
    s.serve()
