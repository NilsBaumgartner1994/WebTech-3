from server.log import log
import server.webserver as webserver
from uuid import uuid4
import re

cookiename = "csrftoken"

class CSRFMiddleware(webserver.Middleware):
    """Add a csrf attribute to request."""

    def __init__(self):
        self.token = "No CSRF Token!"
        super().__init__()

    def process_request(self, request, response):
        """"""
        if self.token == "No CSRF Token!":
            return self.wrong_csrf()
        if request.method == 'POST' or request.method == 'post':
            if cookiename not in request.cookies:
                return self.wrong_csrf()
            if request.cookies[cookiename] == "No CSRF Token!":
                return self.wrong_csrf()
            if not request.cookies[cookiename] == self.token:
                return self.wrong_csrf()
        else:
            if cookiename not in request.cookies:
                self.token = self.create_token()
                response.add_cookie(self.make_cookie(self.token))

    def process_response(self, response):
        """Add CSRF Token"""
        response.add_cookie(self.make_cookie(self.token))

    def create_token(self):
        return "Created Token"

    def make_cookie(self, value):
        """Returns Cookie object for nightmode"""
        return webserver.Cookie("csrftoken", value, path='/')
        #return webserver.Cookie(self.cookiename, value, path='/', expires=webserver.Cookie.expiry_date(30))

    def wrong_csrf(self):
        """ Respond that no Authentification is given/there"""
        log(3, "Wrong CSRF-Token.")
        raise webserver.StopProcessing(403, "Wrong CSRF-Token.")