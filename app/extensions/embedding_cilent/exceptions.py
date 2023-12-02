"""serving client exception """


class BaseProxyError(Exception):
    """ base error for serving client """


class RequestTimeout(BaseProxyError):
    """ raised when request timeout """


class ServiceUnavailableError(BaseProxyError):
    """ raised when response status_code >= 500 """


class ClientSideError(BaseProxyError):
    """ raised when response 200 < status_code < 500 """
