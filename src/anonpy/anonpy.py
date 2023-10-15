#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict, List, Optional, Self, Union, overload

from .endpoint import Endpoint
from .internals import LogHandler, LogLevel, RequestHandler, Timeout, __package__, get_progress_bar, join_url, truncate


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

    def upload(self: Self, path: Union[str, Path], enable_progressbar: bool=False) -> Dict:
        """
        Upload a file. Set `enable_progressbar` to `True` to enable a terminal
        progress indicator.
        """
        MB = 1_048_576
        name = Path(path).name
        size = os.stat(path).st_size
        chunk_size = min(1*MB, size // 2)

        with get_progress_bar() as progress:
            task_id = progress.add_task("Upload", total=size, name=truncate(name, width=40), visible=enable_progressbar)

            with open(path, mode="rb") as file_handler:
                for chunk in iter(lambda: file_handler.read(chunk_size), b""):
                    response = self._post(
                        self.endpoint.upload,
                        files={
                            "file": (name, chunk),
                            "token": self.token,
                        }
                    )
                    progress.update(task_id, advance=len(chunk))

            progress.stop_task(task_id)

        response_data = response.json()

        if url:=response_data.get("url") is None:
            resource = response_data.get("id", "UNKNOWN")
            relative_url = self.endpoint.download.format(resource)
            url = join_url(self.api.geturl(), relative_url)

        self.logger.info("Upload %s to %s", name, url, hide=not self.enable_logging, stacklevel=2)

        return {
            "name": name,
            "folder": path,
            "size": size,
            "resource": resource,
            "url": url,
        }

    def preview(self: Self, resource: str) -> Dict:
        """
        Retrieve meta data about a `resource` without committing to a download.
        """
        url = self.endpoint.preview.format(resource)
        response = self._get(url, allow_redirects=True)
        self.logger.info("Preview: %s", resource, hide=not self.enable_logging, stacklevel=2)
        return response.json()

    @overload
    def download(self: Self, resource: str, path: Union[str, Path]) -> Dict:
        """
        Download a `resource` and save the file to `path`.
        """
        ...

    @overload
    def download(
            self: Self,
            resource: str,
            path: Union[str, Path],
            enable_progressbar: bool,
            size: int,
            name: str,
        ) -> Dict:
        """
        Download a `resource` and save the file to `path`. If `enable_progressbar`
        is set to `True`, also specify the total file `size` and file `name` as
        arguments.

        Raise a `TypeError` exception if the aforementioned rule is violated.
        """
        ...

    def download(
            self: Self,
            resource: str,
            path: Union[str, Path]=Path.cwd(),
            enable_progressbar: bool=False,
            size: Optional[int]=None,
            name: Optional[str]=None,
        ) -> Dict:
        if enable_progressbar and (size is None or name is None):
            raise TypeError("invalid combination of arguments")

        MB = 1_048_576
        relative_path = self.endpoint.download.format(resource)
        url = join_url(self.api.geturl(), relative_path)
        full_path = path / name
        chunk_size = min(1*MB, size // 2)

        with get_progress_bar() as progress:
            task_id = progress.add_task("Download", total=size, name=truncate(name, width=40), visible=enable_progressbar)

            with open(full_path, mode="wb") as file_handler:
                with self._get(relative_path, stream=True) as response:
                    for chunk in response.iter_content(chunk_size):
                        file_handler.write(chunk)
                        progress.update(task_id, advance=len(chunk))

            progress.stop_task(task_id)

        self.logger.info("Download %s to %s", url, full_path, hide=not self.enable_logging, stacklevel=2)

        return {
            "name": name,
            "folder": path,
            "size": size,
            "resource": resource,
            "url": url,
        }
