#!/usr/bin/env python3

import os
import platform
from typing import Dict, List, Self, Tuple
from urllib.request import getproxies

from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry


class RequestHandler:
    """
    RequestHandler
    --------------
    Defines a synchronous request handler class which implements an abstraction
    layer over the `Session` object of the `requests` library for working with
    REST APIs.
    """
    __slots__ = [
        "timeout",
        "total",
        "status_forcelist",
        "backoff_factor",
        "user_agent",
        "proxies"
    ]

    _timeout = (5, 5)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1
    _user_agent = None
    _proxies = None

    def __init__(
            self: Self,
            timeout: Tuple[float, float]=_timeout,
            total: int=_total,
            status_forcelist: List[int]=_status_forcelist,
            backoff_factor: int=_backoff_factor,
            user_agent: str=_user_agent,
            proxies: Dict=_proxies,
    ) -> None:
        self.timeout = timeout
        self.total = total
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent
        self.proxies = proxies

    @staticmethod
    def _build_user_agent(package: str, version: str) -> str:
        """
        Create a faithful user agent.
        """
        username = os.environ.get("USERNAME" if platform.system() == "Windows" else "USER", "N/A")

        return " ".join([
            f"{package}/{version}",
            f"{platform.system()}/{platform.release()}"
            f"CPython/{platform.python_version()}",
            f"username/{username}"
        ])

    @property
    def _retry_strategy(self: Self) -> Retry:
        """
        The retry strategy returns the retry configuration made up of the
        number of total retries, the status forcelist as well as the backoff
        factor. These configurations are required by the `HTTPAdapter` to define
        a retry strategy for unsuccessful requests.
        """
        return Retry(
            total=self.total,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor
        )

    @property
    def _session(self: Self) -> Session:
        """
        Creates a custom `Session` object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the `RequestHandler` methods in form of parameters
        and keyword arguments.
        """
        adapter = HTTPAdapter(max_retries=self._retry_strategy)

        session = Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.hooks["response"] = [lambda response, *args, **kwargs: response.raise_for_status()]
        session.headers.update({
            "User-Agent": self.user_agent
        })
        return session

    def _get(self, url: str, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`. Adds proxies to this session
        on the fly if urllib is able to pick up the system's proxy settings.

        This method will raise an `HTTPError` if the HTTP request returned an
        unsuccessful status code.
        """
        response = self._session.get(
            url,
            timeout=self.timeout,
            proxies=self.proxies or getproxies(),
            allow_redirects=False,
            **kwargs
        )
        response.encoding = "utf-8"
        return response
