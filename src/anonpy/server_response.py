#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Self
from urllib.parse import ParseResult

from .status_codes import StatusCode

@dataclass(frozen=True, slots=True)
class ServerResponse:
    """
    Serializes the response to an object. Almost all properties return `None`
    if the request failed with the exception of `json`, `status` and `status_code`.

    Note that both `file_path` and `ddl` can be `None`, as their existence depends
    on the implementation detail of the invoking method.
    """
    response: Dict
    file_path: Path | None
    ddl: ParseResult | None

    @property
    def json(self: Self) -> Dict:
        """
        Return the entire HTTP response.
        """
        return self.response

    @property
    def status(self: Self) -> bool:
        """
        Return the upload status.
        """
        return bool(self.json.get("status", "false"))

    @property
    def status_code(self: Self) -> StatusCode:
        """
        Return the status code for the current request.

        Note that the enum values don't map to the conventional HTTP error codes.
        """
        if self.status: return StatusCode.OK

        status = StatusCode[self.json["error"]["type"]]
        status.__doc__ = self.json["error"]["message"]
        return status

    #region meta data

    @property
    def url(self: Self) -> str | None:
        """
        Return a (short) URL for the requested file.
        ```
        """
        try:
            return self.json["data"]["file"]["url"]["short"]
        except KeyError:
            return None

    @property
    def url_full(self: Self) -> str | None:
        """
        Return the full URL for the requested file.
        ```
        """
        try:
            return self.json["data"]["file"]["url"]["full"]
        except KeyError:
            return None

    @property
    def id(self: Self) -> str | None:
        """
        Return the ID (path) of the uploaded file.
        """
        try:
            return self.json["data"]["file"]["metadata"]["id"]
        except KeyError:
            return None

    @property
    def name(self: Self) -> Path | None:
        """
        Return the filename of the uploaded file.
        """
        try:
            return Path(self.json["data"]["file"]["metadata"]["name"])
        except KeyError:
            return None

    @property
    def size(self: Self) -> int | None:
        """
        Return the uploaded file size in bytes.
        """
        try:
            return int(self.json["data"]["file"]["metadata"]["size"]["bytes"])
        except KeyError:
            return None

    @property
    def size_readable(self: Self) -> str | None:
        """
        Return a human-readable file size in base 10.
        """
        try:
            return self.json["data"]["file"]["metadata"]["size"]["readable"]
        except KeyError:
            return None

    def __str__(self: Self) -> str:
        return str(self.response)

    #endregion
