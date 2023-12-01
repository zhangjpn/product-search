# -*- coding:utf-8 -*-

from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import text

from . import configs
from .exts import engine, client, auth, product_search_service
from .services.product_search import ProductSearchResult

bp = Blueprint(import_name='product', name='product')


@bp.route(rule='/products', methods=['GET'])
@auth.login_required
def search_products():
    """search products api """

    keywords = request.args.get('kw', default='')
    page = request.args.get('p', type=int, default=1)
    keywords = keywords.strip()
    page_size = configs.PAGINATION_PAGE_SIZE
    page = min(max(1, page), configs.PAGINATION_MAX_ITEMS)

    current_app.logger.debug(
        f'request params: {keywords}, page: {page}, '
        f'page_size: {page_size}'
    )

    has_next = False
    items = []

    if not keywords:
        current_app.logger.warning(f'Keywords required, keywords: {keywords}')

    else:
        result: ProductSearchResult = product_search_service.search_product(
            keywords=keywords,
            page=page,
            page_size=page_size + 1  # used to check if next page exists
        )
        has_next = len(result) > page_size
        for item in result.to_list()[:page_size]:
            items.append(item)
    return jsonify(err_code=0, msg='Success', data={'items': items, 'has_next': int(has_next)})


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
        current_app.logger.info(f'result: {result}')
        conn.commit()

    client.index(index=configs.ES_SEARCH_INDEX, id=product_info['sku'], document=product_info)

    return 'ok'
