from server.log import log
from server.webserver import Middleware, Cookie
from uuid import uuid4
import re


class SessionMiddleware(Middleware):
    """Add a csrf attribute to request."""

    def __init__(self, cookiename="_sessid"):
        super().__init__()

    def process_request(self, request, response):
        """"""
        pass

    def process_response(self, response):
        """"""
        pass

