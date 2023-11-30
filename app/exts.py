# -*- coding:utf-8 -*-
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url, pool_pre_ping=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
pool = ThreadPoolExecutor(10)
logger.info(os.environ)
client = Elasticsearch(
    hosts=os.environ.get('ES_URL'),
    api_key=os.environ.get('ES_API_KEY'),
    verify_certs=False,
    ssl_show_warn=False,
)
