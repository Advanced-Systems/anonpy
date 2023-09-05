#!/usr/bin/env python3

from typing import Dict, List, Optional, Self

from ..anonpy import AnonPy, Timeout
from ..endpoint import Endpoint
from ..internals import RequestHandler


class PixelDrain(AnonPy):
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
        self._api = "https://pixeldrain.com/api/"
        self._endpoint = Endpoint(upload="/file", download="file/{}", preview="/file/{}/info")
        self.enable_logging = enable_logging

        super().__init__(
            self._api,
            endpoint=self._endpoint,
            token=token,
            timeout=timeout,
            total=total,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            user_agent=user_agent,
            proxies=proxies
        )
