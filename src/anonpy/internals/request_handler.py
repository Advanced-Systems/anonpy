#!/usr/bin/env python3

import base64
import os
import platform
from typing import Dict, List, Optional, Self, Tuple
from urllib.parse import urlparse
from urllib.request import getproxies
from warnings import warn

from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

from ..security import SecurityWarning
from .authorization import Authorization
from .timeout import Timeout
from .utils import join_url


class RequestHandler:
    """
    RequestHandler
    --------------
    Defines a synchronous request handler class which implements an abstraction
    layer over the `Session` object of the `requests` library for working with
    REST APIs.
    """
    __slots__ = [
        "api",
        "token",
        "credentials",
        "timeout",
        "total",
        "status_forcelist",
        "backoff_factor",
        "user_agent",
        "proxies",
        "encoding"
    ]

    _timeout = Timeout(5, 5)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1
    _user_agent = None
    _proxies = None

    def __init__(
            self: Self,
            api: str,
            token: Optional[str]=None,
            timeout: Timeout=_timeout,
            total: int=_total,
            status_forcelist: List[int]=_status_forcelist,
            backoff_factor: int=_backoff_factor,
            user_agent: str=_user_agent,
            proxies: Dict=_proxies,
            encoding: str="utf-8"
    ) -> None:
        self.api = urlparse(api)
        self.token = token
        self.credentials = None
        self.timeout = timeout.values
        self.total = total
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent
        self.proxies = proxies or getproxies()
        self.encoding = encoding

    @staticmethod
    def build_user_agent(package: str, version: str, expose_username: bool=False) -> str:
        """
        Create a faithful user agent and expose the following information in the
        user agent:

        - anonpy name and version
        - platform name and version
        - CPython version
        - client username as read from the environment variable
          (only if `expose_username` is enabled)

        Issues a `SecurityWarning` if `expose_username` is enabled.
        """
        user_agent_data = [
            f"{package}/{version}",
            f"{platform.system()}/{platform.release()}"
            f"CPython/{platform.python_version()}"
        ]

        if expose_username:
            warn("potential leak of PII in user agent", category=SecurityWarning, stacklevel=2)
            username = os.environ.get("USERNAME" if platform.system() == "Windows" else "USER", "N/A")
            user_agent_data.append(f"username/{username}")

        return " ".join(user_agent_data)

    def set_credentials(self: Self, auth: Authorization) -> None:
        auth_header = None

        match auth:
            case Authorization.Basic:
                if (self.api.scheme == "http"):
                    warn(message=" ".join([
                        "Base64-encoding can easily be reversed to obtain the original",
                        "name and password, so Basic authentication is completely insecure.",
                        "HTTPS is always recommended when using authentication, but is",
                        "even more so when using Basic authentication."
                    ]), category=SecurityWarning, stacklevel=2)

                self.credentials = base64.b64encode(self.token.encode(self.encoding)).decode(self.encoding)
                auth_header = {"Authorization": f"Basic {self.credentials}"}
            case _:
                raise NotImplementedError()

        self._session.headers.update(auth_header)

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
        Create a custom `Session` object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the `RequestHandler` methods in form of parameters
        and keyword arguments.
        """
        adapter = HTTPAdapter(max_retries=self._retry_strategy)

        session = Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.hooks["response"] = [lambda response, *args, **kwargs: response.raise_for_status()]
        session.headers.update({"User-Agent": self.user_agent})
        return session

    def _get(self: Self, endpoint: str, **kwargs) -> Response:
        """
        Return the GET request, encoded in `utf-8` by default. This method will
        add proxies to this session on the fly if urllib is able to pick up the
        system's proxy settings and verify SSL certificates for HTTPS requests.

        Raise an `HTTPError` if the HTTP request returned an unsuccessful status
        code.
        """
        response = self._session.get(
            url=join_url(self.api.geturl(), endpoint),
            timeout=self.timeout,
            proxies=self.proxies,
            **kwargs
        )
        response.encoding = self.encoding
        return response

    def _post(self, endpoint: str, **kwargs) -> Response:
        """
        Send a POST request and return a `Response` object as a result.
        """
        return self._session.post(
            url=join_url(self.api.geturl(), endpoint),
            timeout=self.timeout,
            proxies=self.proxies,
            verify=True,
            **kwargs
        )

    def _put(self, endpoint: str, **kwargs) -> Response:
        """
        Send a PUT request and return a `Response` object as a result.
        """
        return self._session.put(
            url=join_url(self.api.geturl(), endpoint),
            timeout=self.timeout,
            proxies=self.proxies,
            verify=True,
            **kwargs
        )
