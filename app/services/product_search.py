# -*- coding:utf-8 -*-
"""
A product search service
"""
import logging
import sys
from logging import Logger
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

from app.extensions.embedding_cilent import EmbeddingClient


class ProductSearchBaseError(Exception):
    """base exception for product search module"""


class SearchQueryError(ProductSearchBaseError):
    """raised when unable to query to elasticsearch"""


class ProductResultItem(object):
    def __init__(self, id_, sku, title, description):
        self.id = id_
        self.sku = sku
        self.title = title
        self.description = description

    @classmethod
    def from_dict(cls, dict_):
        return cls(
            id_=dict_['id'],
            sku=dict_['sku'],
            title=dict_['title'],
            description=dict_['description']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'title': self.title,
            'description': self.description
        }


class ProductSearchResult(object):

    def __init__(self, result_data):
        self.result_data = result_data

    @classmethod
    def from_search_response(cls, response: ObjectApiResponse) -> "ProductSearchResult":
        data = response.body['hits']['hits']
        result_data = []
        for item in data:
            product_info = {
                'id': item['_id'],
                'sku': item['_source']['sku'],
                'title': item['_source']['title'],
                'description': item['_source']['description'],
            }
            result_data.append(ProductResultItem.from_dict(product_info))
        result = cls(result_data=result_data)
        return result

    def __len__(self):
        return len(self.result_data)

    def __iter__(self):
        for item in self.result_data:
            yield item

    def to_list(self):
        return [item.to_dict() for item in self.result_data]


class ProductService(object):

    def __init__(
        self,
        index: str,
        es_client: Elasticsearch,
        embedding_client: EmbeddingClient,
        logger: Logger = None,
        timeout=None
    ):

        self.es_client = es_client
        self.embedding_client = embedding_client
        self.index = index
        if logger:
            self.logger = logger
        else:
            self._set_default_logger()
        self.timeout = timeout

    def _set_default_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(fmt=formatter)
        logger.addHandler(handler)
        self.logger = logger

    @staticmethod
    def paginate_parameter(page, page_size):
        """convert pagination into elasticsearch parameters"""
        skip = (page - 1) * page_size
        size = page_size
        return skip, size

    def keyword_search(self, keywords: str, page: int, page_size: int) -> ObjectApiResponse:
        """
        search using keywords for exact match
        :param keywords: (str) user input keywords
        :param page: (int) page number
        :param page_size: (int) size per page
        :return ObjectApiResponse
        """
        skip, size = self.paginate_parameter(page, page_size)
        search_resp: ObjectApiResponse = self.es_client.search(
            index=self.index,
            from_=skip,
            size=size,
            query={
                'match': {
                    'title': {
                        'query': keywords
                    }
                }
            },
            source={
                'excludes': ['embedding']
            },
            timeout=self.timeout
        )
        return search_resp

    def semantic_search(self, query: str, page_size: int) -> ObjectApiResponse:
        """
        search using keywords for semantic match
        :param query: (str) user input
        :param page_size: (int) return document count
        :return: ObjectApiResponse
        """

        # convert query into vector
        query_vector = self.embedding_client.predict(query)

        # knn search
        search_resp: ObjectApiResponse = self.es_client.search(
            index=self.index,
            knn={
                'field': 'embedding',
                'k': page_size,
                'num_candidates': page_size,
                'query_vector': query_vector,
            },
            source={
                'excludes': ['embedding']
            },
            timeout=self.timeout
        )
        return search_resp

    def search_product(self, keywords, page, page_size, backup_page_size) -> ProductSearchResult:
        """
        search product using user input
        :param keywords: (str) user input
        :param page: (int) page number
        :param page_size: (int) size per page
        :param backup_page_size: (int) max return page size when no direct match
        :return ProductSearchResult

        """
        try:
            search_resp = self.keyword_search(keywords, page=page, page_size=page_size)
            resp_data = search_resp.body
            if not resp_data['hits']['hits']:
                search_resp = self.semantic_search(query=keywords, page_size=backup_page_size)
        except Exception as e:
            self.logger.exception(f'Exception was raised when searching for product list, error: {e}')
            raise SearchQueryError(f'Unknown Error occurred') from e

        return ProductSearchResult.from_search_response(search_resp)
