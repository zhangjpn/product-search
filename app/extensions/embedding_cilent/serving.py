import logging
import time
import uuid
from urllib.parse import urljoin

from requests import Response
from requests import Session
from requests.exceptions import Timeout

from .exceptions import RequestTimeout, ServiceUnavailableError, ClientSideError


class EmbeddingClient(object):

    def __init__(self, host, model_name, session: Session = None,
                 logger: logging.Logger = None, timeout=None, headers=None):
        self.host = host
        self.model_name = model_name
        self._session = session or Session()
        self._logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        self.headers = headers or dict()

    def predict(self, query, **kwargs) -> dict:
        """request language model for prediction result """
        pth = f'/v1/models/{self.model_name}:predict'

        body = {"instances": [query]}
        try:

            resp = self.send('POST', path=pth, json=body, **kwargs)
        except Timeout:
            raise RequestTimeout(
                f'Timeout on request, host: {self.host}, path: {pth}, payload: {body}'
            )
        if not resp.ok:
            if resp.status_code < 500:
                raise ClientSideError(
                    f'Service available on request, '
                    f'host: {self.host}, path: {pth}, payload: {body}, '
                    f'status_code: {resp.status_code}, content: {resp.content}'
                )
            else:
                raise ServiceUnavailableError(
                    f'Service available on request, '
                    f'host: {self.host}, path: {pth}, payload: {body}, '
                    f'status_code: {resp.status_code}, content: {resp.content}'
                )
        resp_body = resp.json()
        ret = resp_body.get('predictions')[0]
        self._logger.debug(f'Embedding got result, query:{query}, result: {resp_body}')
        return ret

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
