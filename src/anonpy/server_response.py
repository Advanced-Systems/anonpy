#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from requests.models import Response


@dataclass(frozen=True, slots=True)
class ServerResponse:
    """
    Data class that is primarily used as a structured return type for the upload,
    preview and download methods.
    """
    response: Response
    file_path: Path
    ddl: ParseResult

    @property
    def json(self) -> dict:
        """
        Return the entire HTTP response.
        """
        return self.response.json()

    @property
    def status(self) -> bool:
        """
        Return the upload status.
        """
        return bool(self.json['status'])

    @property
    def url(self) -> ParseResult:
        """
        Return the URL associated with the uploaded file.
        ```
        """
        return urlparse(self.json['data']['file']['url']['full'])

    #region meta data

    @property
    def id(self) -> str:
        """
        Return the ID (path) of the uploaded file.
        """
        return self.json['data']['file']['metadata']['id']

    @property
    def name(self) -> Path:
        """
        Return the filename of the uploaded file.
        """
        return Path(self.json['data']['file']['metadata']['name'])

    @property
    def size(self) -> int:
        """
        Return the uploaded file size in bytes.
        """
        return int(self.json['data']['file']['metadata']['size']['bytes'])

    @property
    def size_readable(self) -> str:
        """
        Return a human-readable file size in base 10.
        """
        return self.json['data']['file']['metadata']['size']['readable']

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID={self.id})"

    #endregion
