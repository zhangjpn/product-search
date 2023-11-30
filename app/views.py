# -*- coding:utf-8 -*-

from datetime import datetime

from flask import Blueprint, request
from sqlalchemy import text

from . import configs
from .exts import engine, logger, client

bp = Blueprint(import_name='product', name='product')


@bp.route(rule='/products', methods=['GET'])
def search_products():
    """search products"""
    return 'ok'


@bp.route(rule='/admin/product', methods=['POST'])
def add_product():
    """add product by merchant or admin user"""

    product_info = request.get_json(silent=True)
    product_info['created_at'] = int(datetime.now().timestamp() * 1000)
    with engine.connect() as conn:
        result = conn.execute(text(
            '''
                INSERT INTO `products`(
                    `sku`, `title`, `description`,`created_at`
                )values(
                    :sku, :title, :description, :created_at
                )
            '''
        ), parameters=product_info)
        logger.info(f'result: {result}')
        conn.commit()

    client.index(index=configs.ES_SEARCH_INDEX, id=product_info['sku'], document=product_info)

    return 'ok'


@bp.route(rule='/admin/product', methods=['PUT'])
def update_product():
    pass


@bp.route(rule='/admin/product', methods=['DELTE'])
def remove_product():
    pass
