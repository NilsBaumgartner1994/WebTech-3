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
        """Check CSRF-Token and create new if necessary"""
        if request.method == 'POST' or request.method == 'post':
            if self.token == "No CSRF Token!":
                return self.wrong_csrf()
            if cookiename not in request.cookies:
                return self.wrong_csrf()
            if request.cookies[cookiename] == "No CSRF Token!":
                return self.wrong_csrf()
            if not request.cookies[cookiename] == self.token:
                return self.wrong_csrf()
            else:
                log(3, "CSRF-Token correct.")
        else:
            if cookiename not in request.cookies or request.cookies[cookiename] == "No CSRF Token!":
                self.token = self.create_token()
                response.add_cookie(self.make_cookie(self.token))

    def process_response(self, response):
        """Add CSRF Token"""
        response.add_cookie(self.make_cookie(self.token))

    def create_token(self):
        """Create new CSRF-Token"""
        return "Created Token"

    def make_cookie(self, value):
        """Returns Cookie object for CSRF"""
        return webserver.Cookie("csrftoken", value, path='/', httpOnly=True)
        #return webserver.Cookie(self.cookiename, value, path='/', httpOnly=True, expires=webserver.Cookie.expiry_date(30))

    def wrong_csrf(self):
        """ Respond that no Authentification is given/there"""
        log(3, "Wrong CSRF-Token.")
        raise webserver.StopProcessing(403, "Wrong CSRF-Token.")