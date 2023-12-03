# -*- coding:utf-8 -*-
"""
The app entry point, always run create_app using `create_app()` function
"""
from logging.config import dictConfig

from flask import Flask, make_response

from . import configs
from .extensions.rate_limit import LimitationExceeded
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
    app.logger.setLevel(configs.LOG_LEVEL)
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
