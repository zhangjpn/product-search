# -*- coding:utf-8 -*-

from flask import Blueprint, request, current_app, make_response

from .services.product_search import ProductSearchResult

bp = Blueprint(import_name='product', name='product')


@bp.route(rule='/products', methods=['GET'])
def search_products():
    """search products view function """

    user_ident = request.headers.get('Authorization')
    configs = current_app.configs

    # user authorization
    current_app.auth.auth_user(user_ident)

    # rate limit
    current_app.rate_limiter.check_user_limit(
        duration=configs.get('RATELIMIT_DURATION'),
        limit_count=configs.get('RATELIMIT_COUNT'),
        user_ident=user_ident,
    )

    # parameter validation
    keywords = request.args.get('kw', default='')
    page = request.args.get('p', type=int, default=1)
    keywords = keywords.strip()
    page_size = configs.PAGINATION_PAGE_SIZE
    page = min(max(1, page), configs.PAGINATION_MAX_ITEMS)

    product_search_service = current_app.product_search_service

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
            page_size=page_size + 1,  # used to check if next page exists
            backup_page_size=page_size  # max return count if no direct match
        )
        has_next = len(result) > page_size
        for item in result.to_list()[:page_size]:
            items.append(item)
    return make_response(dict(err_code=0, msg='Success', data={'items': items, 'has_next': int(has_next)}))
