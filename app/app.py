# -*- coding:utf-8 -*-

from flask import Flask
from .views import bp


def create_app():
    app = Flask(__name__)
    register_error_handler(app)
    register_extensions(app)
    register_resource(app)

    return app


def register_error_handler(app):
    """注册错误处理函数"""

    @app.errorhandler(404)
    def handle_not_found(err):
        """ handle 404 error """
        return dict(err_code=40040, msg='Not found'), 404

    @app.errorhandler(Exception)
    def handle_unknown_error(err):
        app.logger.exception(f'Unknown error was raised：{err}')
        return dict(error_cod=50000, msg='Internal error'), 500


def register_extensions(app):
    pass


def register_resource(app):
    app.register_blueprint(bp)
