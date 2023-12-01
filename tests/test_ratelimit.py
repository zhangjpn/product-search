# -*- coding:utf-8 -*-
"""test ratelimit module"""
from app.services.rate_limit import RateLimiter, parse_duration_from_str


def test_parse_duration_from_str():
    time_str_match = {
        '2d': 2 * 24 * 60 * 60,
        '3m': 3 * 60,
        '10h': 10 * 60 * 60,
        '4s': 4,
    }
    for k, v in time_str_match.items():
        assert parse_duration_from_str(k) == v