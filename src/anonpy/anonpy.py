#!/usr/bin/env python3

import os
import html
import re
from pathlib import Path
from typing import Dict, List, Self, Tuple, Union, Optional, Iterable
from urllib.parse import urljoin, urlparse

from .internals import RequestHandler, LogHandler
from .metadata import __package__, __version__
from .server_response import ServerResponse

from requests_toolbelt import MultipartEncoderMonitor
from tqdm import tqdm

class AnonPy(RequestHandler, LogHandler):
    def __init__(
            self: Self,
            base: str,
            enable_logging: bool=False,
            token: Optional[str] = None,
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

    @staticmethod
    def __progressbar_options(
            iterable: Iterable,
            desc: str,
            unit: str,
            color: str="\033[32m",
            char: str='\u25CB',
            total: int=None,
            disable: bool=False
        ) -> Dict:
        """
        Return custom optional arguments for `tqdm` progressbars.
        """
        return {
            'iterable': iterable,
            'bar_format': "{l_bar}%s{bar}%s{r_bar}" % (color, "\033[0m"),
            'ascii': char.rjust(9, ' '),
            'desc': desc,
            'unit': unit.rjust(1, ' '),
            'unit_scale': True,
            'unit_divisor': 1024,
            'total': len(iterable) if total is None else total,
            'disable': not disable
        }

    @staticmethod
    def __callback(monitor: MultipartEncoderMonitor, tqdm_handler: tqdm) -> None:
        """
        Define a multi part encoder monitor callback function for the upload method.
        """
        tqdm_handler.total = monitor.len
        tqdm_handler.update(monitor.bytes_read - tqdm_handler.n)

    def upload(self: Self, path: Union[str, Path], progressbar: bool=False) -> ServerResponse:
        path = Path(path)
        size = os.stat(path).st_size
        options = AnonPy.__progressbar_options(
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
                    callback=lambda monitor: AnonPy.__callback(monitor, tqdm_handler)
                )

                response = self._session.post(
                    urljoin(self.base, 'upload'),
                    data=encoder_monitor,
                    params={'token': self.token},
                    headers={'Content-Type': encoder_monitor.content_type},
                    timeout=self.timeout,
                    proxies=self.proxies,
                    verify=True
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
        options = AnonPy.__progressbar_options(
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

