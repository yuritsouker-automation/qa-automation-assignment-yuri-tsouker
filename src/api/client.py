from __future__ import annotations

import requests

from src.api.config import ApiConfig


class ApiClient:
    def __init__(self, session: requests.Session, config: ApiConfig):
        self._session = session
        self._config = config

    def get(self, path: str, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", self._config.timeout)
        url = self._config.build_url(path)
        return self._session.get(url, timeout=timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", self._config.timeout)
        url = self._config.build_url(path)
        return self._session.post(url, timeout=timeout, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", self._config.timeout)
        url = self._config.build_url(path)
        return self._session.put(url, timeout=timeout, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", self._config.timeout)
        url = self._config.build_url(path)
        return self._session.delete(url, timeout=timeout, **kwargs)

