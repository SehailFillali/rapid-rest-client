import json
import logging
import os
from urllib.parse import urljoin
from typing import Optional, Mapping

from requests import request

from rest_client.__version__ import __version__
from rest_client.base.authentication import Authentication
from rest_client.base.config import ApiResponse, BaseUrlConfig, RequestConfig
from rest_client.base.util import fill_query_params
from rest_client.base.variables import ENV

log = logging.getLogger(__name__)


class NoEndpointsExceptions(Exception):
    pass


class Client:

    @property
    def endpoints(self) -> dict:
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints):
        self._endpoints = endpoints

    @property
    def base_url_config(self) -> BaseUrlConfig:
        return self._base_url_config

    @base_url_config.setter
    def base_url_config(self, base_url_config: BaseUrlConfig):
        self._base_url_config = base_url_config

    def __init__(
            self,
            authentication_handler: Authentication = None,
            content_type: str = 'application/json;charset=UTF-8',
            user_agent: str = f'rapid-rest-base-client-{__version__}',
            headers: Optional[Mapping] = None,
            ):
        self._endpoints = {}
        self._base_url_config = None
        self.auth = authentication_handler
        self.method: str = 'GET'
        self._headers = headers
        self.content_type = content_type
        self.user_agent = user_agent

    @property
    def headers(self):
        if self._headers:
            return self._headers
        else:
            return {
                'Content-Type': self.content_type,
                'User-Agent': self.user_agent
            }

    def _path(self, path):
        path = path.lstrip('/')
        if os.environ.get(ENV, None) == 'SANDBOX':
            return urljoin(self.base_url_config.sandbox_url, path)
        return urljoin(self.base_url_config.base_url, path)

    def _request(self, data: dict = None, *args, **kwargs) -> ApiResponse:
        data = data or {}
        request_config: RequestConfig = kwargs.pop('request_config')
        log.debug(request_config)

        res = request(
            request_config.method,
            self._path(request_config.path),
            headers=kwargs.pop('headers', self.headers),
            data=json.dumps(data) if request_config.method in (
                'POST', 'PUT', 'PATCH') and data else None,
            params=kwargs,
            auth=self.auth
        )

        return res

    def __getattr__(self, item):
        log.debug(f'Requesting endpoint: {item}')
        log.debug(self.endpoints)

        if self.endpoints.get(item, None):
            def wrapper(*args, **kwargs):
                log.debug('called with %r and %r' % (args, kwargs))
                return self.method_template(self.endpoints.get(item))(*args, **kwargs)

            return wrapper
        raise AttributeError(f'{item} does not exist, possible calls: {self.endpoints.keys()}')

    def method_template(self, _endpoint):
        def fn(*args, **kwargs):
            _endpoint.path = fill_query_params(_endpoint.path, *args)
            kwargs.update({
                'request_config': _endpoint
            })
            return self._request(**kwargs)

        return fn
