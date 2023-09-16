#!/usr/bin/env python3

import csv
import json
import sys
from enum import Enum, unique
from logging import FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Dict, List, Optional, Self, Union

from .json_formatter import JsonFormatter


@unique
class LogLevel(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class LogHandler:
    def __init__(
            self: Self,
            level: LogLevel,
            path: Optional[Union[str, Path]]=None,
            encoding: str="utf-8"
        ) -> None:
        """
        Instantiate a new logger object.
        """
        self.level = level
        self.path = Path(path) if path is not None else None
        self.encoding = encoding

        self.__logger = getLogger(__name__)
        self.__logger.setLevel(level.value)

    def set_base_path(self: Self, path: Union[str, Path]) -> Self:
        """
        Set the log file's base path.
        """
        self.path = Path(path)
        return self

    def add_handler(self: Self, name: Optional[Union[str, Path]]=None) -> Self:
        """
        Add a file handler to this logger instance. If no `name` is specified,
        log output to `stdout` instead.
        """
        formatter = None
        target = Path(name).suffix if name is not None else "console"

        match target:
            case ".log" | ".dat" | ".txt":
                formatter = Formatter(
                    "%(asctime)s [%(levelname)s]::%(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            case ".csv":
                raise NotImplementedError("TODO")
            case ".json":
                formatter = JsonFormatter({
                    "timestamp": "asctime",
                    "level": "levelname",
                    "name": "name",
                    "file": "filename",
                    "line": "lineno",
                    "message": "message"
                })
            case "console":
                console = StreamHandler(sys.stdout)
                formatter = Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
                console.setFormatter(formatter)
                self.__logger.addHandler(console)
                return self
            case _:
                raise NotImplementedError()

        log_file = self.path.joinpath(name)
        log_file.touch(exist_ok=True)
        handler = FileHandler(log_file)
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)
        return self

    def get_log_history(self: Self, name: Union[str, Path]) -> Union[List[str], List[List[str]], Dict[str, Any]]:
        """
        Return the log file content.

        Raise a `FileNotFoundError` if the file doesn't exist.
        """
        target = Path(name).suffix
        file = self.path.joinpath(name)

        if not file.exists():
            raise FileNotFoundError()

        with open(file, mode="r", encoding=self.encoding) as file_handler:
            match target:
                case ".log" | ".dat" | ".txt":
                    return file_handler.readlines()
                case ".csv":
                    return [row for row in csv.reader(file_handler)]
                case ".json":
                    # The JsonFormatter appends records on a line-by-line basis,
                    # which is why it's not possible to save the log file as a
                    # valid JSON file on write
                    lines = ",".join(file_handler.readlines()).replace('\n', '')
                    return json.loads(f"[{lines}]")
                case _:
                    raise NotImplementedError()

    #region log utilities

    def log(
            self: Self,
            level: LogLevel,
            message: str,
            *args: object,
            hide: bool=False
        ) -> None:
        """
        Log `message % args` with severity `level`.
        """
        if not hide: self.__logger.log(level.value, message, *args)

    def debug(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.DEBUG`.
        """
        if not hide: self.__logger.debug(message, *args)

    def info(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.INFO`.
        """
        if not hide: self.__logger.info(message, *args)

    def warning(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.WARNING`.
        """
        if not hide: self.__logger.warning(message, *args)

    def error(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.ERROR`.
        """
        if not hide: self.__logger.error(message, *args)

    def critical(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.CRITICAL`.
        """
        if not hide: self.__logger.critical(message, *args)

    #endregion
