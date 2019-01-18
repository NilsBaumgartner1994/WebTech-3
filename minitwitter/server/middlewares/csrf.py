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
        pass

    def process_response(self, response):
        """Add CSRF Token"""
        response.add_cookie(self.make_cookie(self.token))

    def make_cookie(self, value):
        """Returns Cookie object for nightmode"""
        return webserver.Cookie("csrftoken", value, path='/')
        #return webserver.Cookie(self.cookiename, value, path='/', expires=webserver.Cookie.expiry_date(30))