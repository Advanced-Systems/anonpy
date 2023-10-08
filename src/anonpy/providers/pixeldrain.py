#!/usr/bin/env python3

from typing import Dict, List, Optional, Self

from ..anonpy import AnonPy, Timeout
from ..endpoint import Endpoint
from ..internals import Authorization, RequestHandler


class PixelDrain(AnonPy):
    __slots__ = [
        "api",
        "token",
        "credentials",
        "endpoint",
        "enable_logging",
        "logger",
        "timeout",
        "total",
        "status_forcelist",
        "backoff_factor",
        "user_agent",
        "proxies",
        "encoding"
    ]

    def __init__(
            self: Self,
            user_agent: str,
            token: Optional[str]=None,
            enable_logging: bool=False,
            timeout: Timeout=Timeout(0.5, 1),
            total: int=RequestHandler._total,
            status_forcelist: List[int]=RequestHandler._status_forcelist,
            backoff_factor: int=RequestHandler._backoff_factor,
            proxies: Dict=RequestHandler._proxies
        ) -> None:
        api = "https://pixeldrain.com/api/"
        endpoint = Endpoint(upload="/file", download="file/{}", preview="/file/{}/info")

        super().__init__(
            api=api,
            endpoint=endpoint,
            token=token,
            enable_logging=enable_logging,
            timeout=timeout,
            total=total,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            user_agent=user_agent,
            proxies=proxies
        )

        if token: self.set_credentials(Authorization.Basic)
