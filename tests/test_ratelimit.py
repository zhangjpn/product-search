# -*- coding:utf-8 -*-
"""test ratelimit module"""
import time

import pytest

from app.extensions.rate_limit import parse_duration_from_str, RateLimiter, LimitationExceeded


def test_parse_duration_from_str():
    time_str_match = {
        '2d': 2 * 24 * 60 * 60,
        '3m': 3 * 60,
        '10h': 10 * 60 * 60,
        '4s': 4,
    }
    for k, v in time_str_match.items():
        assert parse_duration_from_str(k) == v


def test_rate_limit(redis_cli):
    limiter = RateLimiter(redis_client=redis_cli)

    @limiter.register_identity_getter
    def id_getter():
        return 'ident1'

    duration = '5s'
    counter_key = limiter.get_cache_key(type_='counter', duration=duration, ident='ident1')
    redis_cli.delete(counter_key)

    @limiter.limit(duration, 10)
    def sleep(secs: float):
        time.sleep(secs)

    for i in range(1, 12):

        if i == 11:
            with pytest.raises(LimitationExceeded) as exc_info:
                sleep(0.2)
        else:
            sleep(0.2)
            assert int(redis_cli.get(counter_key)) == i
