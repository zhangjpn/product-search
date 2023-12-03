# -*- coding:utf-8 -*-
""" a api rate limit utils """
import re
from functools import wraps

from redis.client import Redis


class RateLimitBaseError(Exception):
    """rate limit base error, all error relative to rate limit should derive from it"""


class LimitationExceeded(RateLimitBaseError):

    def __init__(self, message, duration, limit_count):
        super(LimitationExceeded, self).__init__(message)
        self.duration = duration
        self.limit_count = limit_count


class IdentityGetterNotSet(RateLimitBaseError):
    """raised if identity_getter method not set"""


class InvalidDurationFormat(RateLimitBaseError):
    """raised if duration format is invalid."""


class InvalidIdentity(RateLimitBaseError):
    """raised if identity is invalid."""


DURATION_PATTERN = re.compile(r'^(\d+)([dhms])$')

TIME_MAPPING = {
    'd': 24 * 60 * 60,
    'h': 60 * 60,
    'm': 60,
    's': 1,
}


def parse_duration_from_str(time_str) -> int:
    """parse `time_str` into seconds, supported format
    includes {}d, {}h, {}m, {}s. `{}` stands for positive int.
    examples: 1d, 4h, 1m, 10s
    """

    match = DURATION_PATTERN.match(time_str)
    if not match or int(match.groups()[0]) <= 0:
        raise InvalidDurationFormat(f'Invalid duration string: {time_str}')
    count, unit = match.groups()
    count = int(count)

    return int(count) * TIME_MAPPING[unit]


class RateLimiter(object):
    """rate limit decorator
    """
    key_template = '{prefix}.{type}.{duration}:{ident}'

    def __init__(self, redis_client: Redis, identity_getter=None, key_prefix='ratelimit'):
        self.redis_client = redis_client
        self.identity_getter = identity_getter
        self.key_prefix = key_prefix

    def get_cache_key(self, type_, duration, ident):
        return self.key_template.format(
            prefix=self.key_prefix,
            type=type_,
            duration=duration,
            ident=ident
        )

    def handle_limit_exceeded(self):
        raise

    def limit(self, duration, limit_count):
        """
        limit `count` in `duration`
        """

        def wrapper(f):
            @wraps(f)
            def inner(*args, **kwargs):
                if not self.identity_getter:
                    raise IdentityGetterNotSet('Identity not set')
                ident = self.identity_getter()
                if not ident:
                    raise InvalidIdentity(f'Invalid identity: {ident}')
                lock_key = self.get_cache_key(type_='lock', duration=duration, ident=ident)
                counter_key = self.get_cache_key(type_='counter', duration=duration, ident=ident)

                duration_secs = parse_duration_from_str(duration)

                with self.redis_client.lock(lock_key):  # lock to avoid race condition
                    visit_count = self.redis_client.get(counter_key)
                    if not visit_count:
                        self.redis_client.setex(name=counter_key, time=duration_secs, value=1)
                    else:
                        visit_count = int(visit_count)
                        if visit_count >= limit_count:
                            raise LimitationExceeded(
                                f'Reached rate limitation, duration:{duration}, '
                                f'limit:{limit_count}, visit_count: {visit_count}',
                                duration=duration,
                                limit_count=limit_count
                            )
                        else:
                            self.redis_client.incr(counter_key, amount=1)

                return f(*args, **kwargs)

            return inner

        return wrapper

    def register_identity_getter(self, func):
        self.identity_getter = func
        return func