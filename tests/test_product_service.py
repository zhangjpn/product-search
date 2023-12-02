# -*- coding:utf-8 -*-
import logging
import os

from app.services.product_search import ProductService


def test_keyword_search(embedding_client, es_client):
    service = ProductService(
        index=os.environ.get('ES_SEARCH_INDEX'),
        es_client=es_client,
        embedding_client=embedding_client
    )
    match_kw = 'Occur'
    missed_kw = '1Occur'
    match_result = service.keyword_search(keywords=match_kw, page=1, page_size=20)
    assert len(match_result.body['hits']['hits']) == 1
    assert match_result.body['hits']['hits'][0]['_source']['sku'] == 'a1701459854'

    missed_result = service.keyword_search(keywords=missed_kw, page=1, page_size=20)
    assert len(missed_result.body['hits']['hits']) == 0


def test_semantic_search(embedding_client, es_client):
    service = ProductService(
        index=os.environ.get('ES_SEARCH_INDEX'),
        es_client=es_client,
        embedding_client=embedding_client,
        logger=logging.getLogger(),
    )

    missed_kw = '1Occur'
    missed_result = service.keyword_search(keywords=missed_kw, page=1, page_size=20)
    assert len(missed_result.body['hits']['hits']) == 0

    semantic_result = service.semantic_search(query=missed_kw, page_size=3)
    assert len(semantic_result.body['hits']['hits']) == 3


def test_search_product(es_client, embedding_client):
    service = ProductService(
        index=os.environ.get('ES_SEARCH_INDEX'),
        es_client=es_client,
        embedding_client=embedding_client,
        logger=logging.getLogger(),
    )

    missed_kw = '1Occur'
    missed_result = service.keyword_search(keywords=missed_kw, page=1, page_size=20)
    assert len(missed_result.body['hits']['hits']) == 0

    product_result = service.search_product(keywords=missed_kw, page=1, page_size=20, backup_page_size=3)
    assert len(product_result) == 3

