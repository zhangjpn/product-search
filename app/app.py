# -*- coding:utf-8 -*-

from flask import Flask
from .views import bp


def create_app():
    app = Flask(__name__)
    register_error_handler(app)
    register_extensions(app)
    register_resource(app)
    app.register_blueprint(bp)
    return app


def register_error_handler(app):
    pass


def register_extensions(app):
    pass


def register_resource(app):
    pass
