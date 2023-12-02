# -*- coding:utf-8 -*-
""" test api """
import os

from flask import Flask
from redis.client import Redis

from app import configs
from app.extensions.rate_limit import RateLimiter


def test_search_product(app: Flask):
    test_client = app.test_client()
    match_kw = 'Occur'
    missed_kw = '1Occur'
    resp = test_client.get('/products', query_string={'kw': match_kw, 'p': 1})
    assert resp.status_code == 403

    resp = test_client.get(
        '/products',
        query_string={'kw': match_kw, 'p': 1},
        headers={
            'Authorization': os.environ.get('SEARCH_API_KEY')
        }
    )
    assert resp.status_code == 200

    assert isinstance(resp.get_json().get('data'), dict)
    assert len(resp.get_json()['data']['items']) == 1

    resp = test_client.get(
        '/products',
        query_string={'kw': missed_kw, 'p': 1},
        headers={
            'Authorization': os.environ.get('SEARCH_API_KEY')
        }
    )
    assert resp.status_code == 200
    assert len(resp.get_json()['data']['items']) == configs.PAGINATION_PAGE_SIZE


def test_api_rate_limit(redis_cli: Redis, app: Flask):
    test_client = app.test_client()
    match_kw = 'Occur'
    duration = os.environ.get('RATELIMIT_DURATION')
    count = int(os.environ.get('RATELIMIT_COUNT'))
    assert count == 10
    assert duration == '5s'

    def ident_getter():
        return os.environ.get('SEARCH_API_KEY')

    limiter = RateLimiter(redis_client=redis_cli, identity_getter=ident_getter)
    counter_key = limiter.get_cache_key(type_='counter', ident=ident_getter(), duration=duration)
    redis_cli.delete(counter_key)

    for i in range(1, 15):
        resp = test_client.get(
            '/products',
            query_string={'kw': match_kw, 'p': 1},
            headers={
                'Authorization': os.environ.get('SEARCH_API_KEY')
            }
        )
        if i < 11:
            assert resp.status_code == 200
            assert isinstance(resp.get_json().get('data'), dict)
            assert len(resp.get_json()['data']['items']) == 1
        else:
            assert resp.status_code == 400
            assert resp.get_json()['err_code'] == 40001

    redis_cli.delete(counter_key)
