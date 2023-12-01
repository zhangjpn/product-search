# -*- coding:utf-8 -*-
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from flask import jsonify, request
from redis.client import Redis
from redis.connection import ConnectionPool
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch

from . import configs
from .extensions.api_auth import ApiAuthExt
from .services.product_search import ProductService
from .services.rate_limit import RateLimiter

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url, pool_pre_ping=True)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
pool = ThreadPoolExecutor(10)
client = Elasticsearch(
    hosts=os.environ.get('ES_URL'),
    api_key=os.environ.get('ES_API_KEY'),
    verify_certs=False,
    ssl_show_warn=False,
)

redis_cli = Redis(
    host=configs.REDIS_HOST,
    port=configs.REDIS_PORT,
    db=configs.REDIS_DB,
    connection_pool=ConnectionPool(max_connections=configs.REDIS_MAX_CONNECTION)
)


def api_key_getter():
    return request.headers.get('Authorization')


def permission_denied_handler():

    return dict(error_cod=40000, msg='Permission denied'), 403


auth = ApiAuthExt(configs.SEARCH_API_KEY)
rate_limiter = RateLimiter(redis_client=redis_cli)

rate_limiter.register_identity_getter(api_key_getter)
auth.register_key_getter(api_key_getter)
auth.register_forbid_handler(permission_denied_handler)

product_search_service = ProductService(
    es_client=client,
    logger=logger,
    index=configs.ES_SEARCH_INDEX,
    timeout=configs.ES_SEARCH_TIMEOUT or None,
)

