# -*- coding:utf-8 -*-
import os
from redis.client import Redis
from elasticsearch import Elasticsearch
import pytest
from dotenv import load_dotenv

from app.app import create_app
from app.extensions.embedding_cilent import EmbeddingClient

load_dotenv()


@pytest.fixture
def es_client():
    yield Elasticsearch(hosts=[os.environ.get('ES_URL')])


@pytest.fixture
def redis_cli():
    yield Redis()


@pytest.fixture
def embedding_client():
    yield EmbeddingClient(
        host=os.environ.get('EMBEDDING_SERVICE_HOST'),
        model_name=os.environ.get('EMBEDDING_SERVICE_HOST_MODEL_NAME')
    )


@pytest.fixture
def app():
    yield create_app()
