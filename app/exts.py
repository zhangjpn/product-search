# -*- coding:utf-8 -*-
import logging
import sys

from elasticsearch import Elasticsearch
from flask import request, make_response
from redis.client import Redis
from redis.connection import ConnectionPool

from . import configs
from .extensions.api_auth import ApiAuthExt
from .extensions.embedding_cilent import EmbeddingClient
from .extensions.rate_limit import RateLimiter
from .services.product_search import ProductService

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

es_client = Elasticsearch(hosts=[configs.ES_HOST])

embedding_client = EmbeddingClient(
    host=configs.EMBEDDING_SERVICE_HOST,
    model_name=configs.EMBEDDING_SERVICE_HOST_MODEL_NAME
)

redis_cli = Redis(
    connection_pool=ConnectionPool(
        max_connections=configs.REDIS_MAX_CONNECTION,
        host=configs.REDIS_HOST,
        port=configs.REDIS_PORT,
        db=configs.REDIS_DB,
    )
)


def api_key_getter():
    return request.headers.get('Authorization')


def permission_denied_handler():
    return make_response(dict(err_code=40003, msg='Permission denied', data={}), 403)


auth = ApiAuthExt(configs.SEARCH_API_KEY)
rate_limiter = RateLimiter(redis_client=redis_cli)

rate_limiter.register_identity_getter(api_key_getter)
auth.register_key_getter(api_key_getter)
auth.register_forbid_handler(permission_denied_handler)

product_search_service = ProductService(
    es_client=es_client,
    embedding_client=embedding_client,
    logger=logger,
    index=configs.ES_SEARCH_INDEX,
    timeout=configs.ES_SEARCH_TIMEOUT or None,
)

