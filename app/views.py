# -*- coding:utf-8 -*-

from flask import Blueprint, request
from .exts import engine, logger
from sqlalchemy import text
bp = Blueprint(import_name='product', name='product')


@bp.route(rule='/products', methods=['GET'])
def search_products():
    """search products"""
    return 'ok'


@bp.route(rule='/admin/product', methods=['POST'])
def add_product():
    """add product by merchant or admin user"""
    return 'ok'


@bp.route(rule='/admin/product', methods=['PUT'])
def update_product():
    pass


@bp.route(rule='/admin/product', methods=['DELTE'])
def remove_product():
    pass
