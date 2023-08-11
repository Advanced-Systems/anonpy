#!/usr/bin/env python3

import html
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Self, Tuple, Union
from urllib.parse import urljoin, urlparse

from requests_toolbelt import MultipartEncoderMonitor
from tqdm import tqdm

from .internals import LogHandler, RequestHandler, _callback, _progressbar_options
from .metadata import __package__, __version__
from .server_response import ServerResponse


class AnonPy(RequestHandler, LogHandler):
    def __init__(
            self: Self,
            base: str,
            token: Optional[str] = None,
            enable_logging: bool=False,
            timeout: Tuple[float, float]=RequestHandler._timeout,
            total: int=RequestHandler._total,
            status_forcelist: List[int]=RequestHandler._status_forcelist,
            backoff_factor: int=RequestHandler._backoff_factor,
            user_agent: str=RequestHandler._user_agent,
            proxies: Dict=RequestHandler._proxies,
        ) -> None:
        super().__init__(
            timeout=timeout,
            total=total,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            user_agent=user_agent,
            proxies=proxies
        )
        self.base = base
        self.enable_logging = enable_logging
        self.token = token

    def upload(self: Self, path: Union[str, Path], progressbar: bool=False) -> ServerResponse:
        path = Path(path)
        size = os.stat(path).st_size
        options = _progressbar_options(
            None,
            f"Upload: {path.name}",
            unit='B',
            total=size,
            disable=progressbar
        )

        with open(path, mode='rb') as file_handler:
            fields = {'file': (path.name, file_handler, 'application/octet-stream')}

            with tqdm(**options) as tqdm_handler:
                encoder_monitor = MultipartEncoderMonitor.from_fields(
                    fields,
                    callback=lambda monitor: _callback(monitor, tqdm_handler)
                )

                response = self._post(
                    urljoin(self.base, 'upload'),
                    data=encoder_monitor,
                    params={'token': self.token},
                    headers={'Content-Type': encoder_monitor.content_type},
                )
                # TODO: configure logging
                return ServerResponse(response.json(), path, None)

    def preview(self: Self, url: str, path: Union[str, Path]=Path.cwd()) -> ServerResponse:
        with self._get(urljoin(self.base, f"v2/file/{urlparse(url).path.split('/')[1]}/info")) as response:
            links = re.findall(r'''.*?(?:href|value)=['"](.*?)['"].*?''', html.unescape(self._get(url).text), re.I)
            ddl = urlparse(next(filter(lambda link: 'cdn-' in link, links)))
            file_path = Path(path).joinpath(Path(ddl.path).name)
            # TODO: configure logging
            return ServerResponse(response.json(), file_path, ddl)

    def download(self: Self, url: str, path: Union[str, Path]=Path.cwd(), progressbar: bool=False) -> ServerResponse:
        MB = 1_048_576
        download = self.preview(url, path)
        options = _progressbar_options(
            None,
            f"Download {download.id}",
            unit='B',
            total=download.size,
            disable=progressbar
        )

        with open(download.file_path, mode='wb') as file_handler:
            with tqdm(**options) as tqdm_handler:
                with self._get(download.ddl.geturl(), stream=True) as response:
                    for chunk in response.iter_content(chunk_size=1*MB):
                        tqdm_handler.update(len(chunk))
                        file_handler.write(chunk)

        # TODO: configure logging
        return download
