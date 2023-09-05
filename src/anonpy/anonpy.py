#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict, List, Optional, Self, Tuple, Union

from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from .endpoint import Endpoint
from .internals import LogHandler, RequestHandler, Timeout, _progressbar_options
from .metadata import __package__, __version__


class AnonPy(RequestHandler, LogHandler):
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
        ) -> None:
        super().__init__(
            api=api,
            token=token,
            timeout=timeout,
            total=total,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            user_agent=user_agent,
            proxies=proxies
        )
        self.endpoint = endpoint
        self.enable_logging = enable_logging

    def upload(self: Self, path: Union[str, Path], progressbar: bool=False) -> Dict:
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

                # TODO: configure logging
                return response.json()

    def preview(self: Self, resource: str) -> Dict:
        response = self._get(self.endpoint.preview.format(resource), allow_redirects=True)
        return response.json()

    def download(
            self: Self,
            resource: str,
            path: Union[str, Path]=Path.cwd(),
            progressbar: bool=False
        ) -> Dict:
        MB = 1_048_576
        info = self.preview(resource)

        options = _progressbar_options(
            None,
            f"Download {info.get('id', 'N/A')}",
            unit="B",
            total=info.get("size", 0),
            disable=progressbar
        )

        with open(path.joinpath(info.get("name", "N/A")), mode="wb") as file_handler:
            with tqdm(**options) as tqdm_handler:
                with self._get(self.endpoint.download.format(resource), stream=True) as response:
                    for chunk in response.iter_content(chunk_size=1*MB):
                        tqdm_handler.update(len(chunk))
                        file_handler.write(chunk)

        # TODO: configure logging
        return info
