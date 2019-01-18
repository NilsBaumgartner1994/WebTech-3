from server.log import log
import server.webserver as webserver
from pprint import pprint
from uuid import uuid4
import re

cookiename = "csrftoken"

class CSRFMiddleware(webserver.Middleware):
    """Add a csrf attribute to request."""

    def __init__(self):
        self.token = None
        self.sessid = None
        super().__init__()

    def process_request(self, request, response):
        """Check CSRF-Token and create new if necessary"""
        if not request.session.sessid:
            self.sessid = None
            self.token = None
            log(3, "No Session.")
            return False
        if (not self.sessid) or self.sessid != request.session.sessid:
            self.sessid = request.session.sessid
            self.token = self.create_token()
        if request.method == 'POST' or request.method == 'post':
            pprint(request.params)
            if not self.token:
                return self.wrong_csrf()
            if cookiename not in request.params and cookiename not in request.headers:
                return self.wrong_csrf()
            if cookiename in request.params and request.params[cookiename] != self.token:
                return self.wrong_csrf()
            if cookiename in request.headers and request.headers[cookiename] != self.token:
                return self.wrong_csrf()
            else:
                log(3, "CSRF-Token correct.")

    def process_response(self, response):
        """Add CSRF Token"""
        if self.token:
            response.add_cookie(self.make_cookie(self.token))
        else:
            response.add_cookie(self.delete_cookie())

    def create_token(self):
        """Create new CSRF-Token"""
        return self.sessid + uuid4().hex

    def make_cookie(self, value):
        """Returns Cookie object for CSRF"""
        return webserver.Cookie(cookiename, value, path='/', httpOnly=False)

    def delete_cookie(self):
        """Returns Expired Cookie object for CSRF"""
        return webserver.Cookie(cookiename, "", path='/', httpOnly=True, expires=webserver.Cookie.expiry_date(-1))

    def wrong_csrf(self):
        """ Respond that no Authentification is given/there"""
        log(3, "Wrong CSRF-Token.")
        raise webserver.StopProcessing(403, "Wrong CSRF-Token.")