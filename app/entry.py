# -*- coding:utf-8 -*-
"""
The app entry point, always run create_app using `create_app()` function
"""
from logging.config import dictConfig
import logging


from flask import Flask, make_response, request
from elasticsearch import Elasticsearch
from .extensions.embedding_client import EmbeddingClient
from redis import Redis, ConnectionPool
from .extensions.api_auth import ApiAuthExt
from .extensions.rate_limit import RateLimiter

from . import configs
from .extensions.rate_limit import LimitationExceeded
from .services.product_search import ProductService
from .views import bp


def create_app():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': configs.LOG_LEVEL,
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)
    logger = logging.getLogger()
    app.logger = logger
    app.logger.setLevel(configs.LOG_LEVEL)
    es_client = Elasticsearch(hosts=[configs.ES_HOST])
    embedding_client = EmbeddingClient(
        host=configs.EMBEDDING_SERVICE_HOST,
        model_name=configs.EMBEDDING_SERVICE_HOST_MODEL_NAME
    )
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
    app.product_search_service = product_search_service
    app.rate_limiter = rate_limiter
    app.auth = auth

    register_error_handler(app)
    register_extensions(app)
    register_resource(app)

    return app


def register_error_handler(app):
    """ register error handler """

    @app.errorhandler(404)
    def handle_not_found(err):
        """ handle 404 error """
        return make_response(dict(err_code=40040, msg='Not found', data={}), 404)

    @app.errorhandler(Exception)
    def handle_unknown_error(err):
        app.logger.exception(f'Unknown error was raised：{err}')
        return make_response(dict(err_code=50000, msg='Internal error'), 500)

    @app.errorhandler(LimitationExceeded)
    def handle_rate_limit_exceeded(err):
        return make_response(dict(err_code=40001, msg='Reached rate limit'), 400)


def register_extensions(app):
    pass


def register_resource(app):
    app.register_blueprint(bp)
