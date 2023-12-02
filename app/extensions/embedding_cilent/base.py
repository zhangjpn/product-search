# -*- coding:utf-8 -*-
""" base http request client """

import logging
import time
import uuid
from urllib.parse import urljoin

from requests import Response
from requests import Session


class BaseClient(object):

    def __init__(self, host, session: Session = None,
                 logger: logging.Logger = None, timeout=None, headers=None):
        self.host = host
        self._session = session or Session()
        self._logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        self.headers = headers or dict()

    def send(self, method, path, params=None, data=None, json=None, **kwargs) -> Response:
        kwargs.setdefault('timeout', self.timeout)
        url = urljoin(self.host, path)
        headers: dict = dict()
        headers.update(self.headers)
        headers.update(kwargs.pop('headers', {}))
        req_id = uuid.uuid4()
        self._logger.debug(f'{self} send request, req_id: {req_id}, url: {url}, method: {method}, '
                           f'headers: {headers}, params: {params}, json: {json} ')
        req_start_time = time.time()
        resp = self._session.request(method, url=url, params=params, data=data, json=json, headers=headers, **kwargs)
        req_end_time = time.time()
        self._logger.debug(f'{self} got response, req_id: {req_id}, time used: {req_end_time - req_start_time}s, '
                           f'url: {url}, method: {method}, '
                           f'status_code: {resp.status_code}, resp body: {resp.text}')

        return resp

    def __repr__(self):
        return f'{self.__class__.__name__}(host={self.host})'

