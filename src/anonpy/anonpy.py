#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict, List, Optional, Self, Union

from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from .endpoint import Endpoint
from .internals import LogHandler, LogLevel, RequestHandler, Timeout, __package__, _progressbar_options


class AnonPy(RequestHandler):
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
            api: str,
            endpoint: Endpoint,
            token: Optional[str]=None,
            enable_logging: bool=False,
            timeout: Timeout=RequestHandler._timeout,
            total: int=RequestHandler._total,
            status_forcelist: List[int]=RequestHandler._status_forcelist,
            backoff_factor: int=RequestHandler._backoff_factor,
            user_agent: str=RequestHandler._user_agent,
            proxies: Dict=RequestHandler._proxies,
            encoding: str="utf-8"
        ) -> None:
        """
        Establish a connection to a REST server by specifying an `Endpoint`.

        Set `enable_logging` to `True` and attach a handler to this logger instance
        to enable method logging on DEBUG level.

        ### Note
        To authenticate requests with a `token`, use the `set_credentials` method:

        ### Example
        ```python
        from anonpy import Authorization, AnonPy, Endpoint

        api = "https://pixeldrain.com/api/"
        endpoint = Endpoint(upload="/file", download="file/{}", preview="/file/{}/info")

        # create a authenticated session
        anon = AnonPy(api, endpoint, token="REDACTED")
        anon.set_credentials(Authorization.Basic)

        # attach console log handler
        anon.enable_logging = True
        anon.logger.add_handler(None)
        ```
        """
        super().__init__(
            api=api,
            token=token,
            timeout=timeout,
            total=total,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            user_agent=user_agent,
            proxies=proxies,
            encoding=encoding
        )

        self.endpoint = endpoint
        self.enable_logging = enable_logging
        self.logger = LogHandler(level=LogLevel.INFO)

    def upload(self: Self, path: Union[str, Path], progressbar: bool=False) -> Dict:
        """
        Upload a file. Set `progressbar` to `True` to enable a terminal progress indicator.
        """
        path = Path(path)
        file = path.name
        size = os.stat(path).st_size
        options = _progressbar_options(
            None,
            f"Upload: {file}",
            unit="B",
            total=size,
            disable=progressbar
        )

        with open(path, mode="rb") as file_handler:
            with tqdm(**options) as tqdm_handler:
                response = self._post(
                    self.endpoint.upload,
                    params={"token": self.token},
                    files={"file": CallbackIOWrapper(tqdm_handler.update, file_handler, "read")}
                )

                self.logger.info("Download: %s", file, hide=not self.enable_logging)
                return response.json()

    def preview(self: Self, resource: str) -> Dict:
        """
        Retrieve meta data about a `resource` without committing to a download.
        """
        url = self.endpoint.preview.format(resource)
        response = self._get(url, allow_redirects=True)
        self.logger.info("Preview: %s", resource, hide=not self.enable_logging)
        return response.json()

    def download(
            self: Self,
            resource: str,
            path: Union[str, Path]=Path.cwd(),
            progressbar: bool=False
        ) -> Dict:
        """
        Download a file. Set `progressbar` to `True` to enable a terminal progress indicator.
        """
        MB = 1_048_576
        preview = self.preview(resource)
        url = self.endpoint.download.format(resource)
        options = _progressbar_options(
            None,
            f"Download {preview.get('id', 'N/A')}",
            unit="B",
            total=preview.get("size", 0),
            disable=progressbar
        )

        with open(path.joinpath(preview.get("name", "N/A")), mode="wb") as file_handler:
            with tqdm(**options) as tqdm_handler:
                with self._get(url, stream=True) as response:
                    for chunk in response.iter_content(chunk_size=1*MB):
                        tqdm_handler.update(len(chunk))
                        file_handler.write(chunk)

        self.logger.info("Upload: %s", url, hide=not self.enable_logging)
        return preview
