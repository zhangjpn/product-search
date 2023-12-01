# -*- coding:utf-8 -*-
from functools import wraps


class ApiAuthBaseError(Exception):
    """base exception for api auth extension"""


class KeyGetterNotSet(ApiAuthBaseError):
    """raised if key_getter method not set"""


class ApiAuthExt(object):
    """flask extension for api key auth"""

    def __init__(self, api_key):
        self.forbid_handler = None
        self.key_getter = None
        self.api_key = api_key

    def register_key_getter(self, f):
        self.key_getter = f
        return f

    def login_required(self, f):
        """
        decorate request handler to check if correct api key is provided.

        """

        @wraps(f)
        def inner(*args, **kwargs):
            if not self.key_getter:
                raise KeyGetterNotSet('key_getter method not set')
            print('cccccccc')
            key = self.key_getter()
            if self.api_key != key and self.forbid_handler:
                print('bbbbbbbb')
                print(self.forbid_handler)
                return self.forbid_handler()
            print('aaaaaaaaa')
            return f(*args, **kwargs)

        return inner

    def register_forbid_handler(self, func):
        """set handler to response for request without correct api key"""
        self.forbid_handler = func
        return func
