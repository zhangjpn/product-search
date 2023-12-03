# -*- coding:utf-8 -*-
""" wrapper client for embedding service REST API """
from .exceptions import ServiceUnavailableError, RequestTimeout, BaseProxyError
from .serving import EmbeddingClient
