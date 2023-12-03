# -*- coding:utf-8 -*-
import os

# elasticsearch rest api connection settings
ES_HOST = os.environ.get('ES_HOST')
ES_SEARCH_INDEX = os.environ.get('ES_SEARCH_INDEX')
ES_SEARCH_TIMEOUT = int(os.environ.get('ES_SEARCH_TIMEOUT', 0))

# product search api settings
PAGINATION_PAGE_SIZE = int(os.environ.get('PAGINATION_PAGE_SIZE', 10))
PAGINATION_MAX_ITEMS = 10000
PAGINATION_MAX_PAGE = PAGINATION_MAX_ITEMS // PAGINATION_PAGE_SIZE

# redis connection settings
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_MAX_CONNECTION = int(os.environ.get('REDIS_MAX_CONNECTION', 1000))

# product search api key
SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY', 'secret-key-you-never-know')

# embedding service rest api connection settings
EMBEDDING_SERVICE_HOST = os.environ.get('EMBEDDING_SERVICE_HOST', 'http://localhost:8501')
EMBEDDING_SERVICE_HOST_MODEL_NAME = os.environ.get('EMBEDDING_SERVICE_HOST_MODEL_NAME')

# rate limit settings
RATELIMIT_DURATION = os.environ.get('RATELIMIT_DURATION', '1d')
RATELIMIT_COUNT = int(os.environ.get('RATELIMIT_COUNT', 100))
