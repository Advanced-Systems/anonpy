#!/usr/bin/env python3

import sys
from enum import Enum, unique
from logging import FileHandler, Formatter, getLogger, StreamHandler
from pathlib import Path
from typing import Self, Union, Optional

@unique
class LogLevel(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class LogHandler:
    def __init__(self: Self, path: Union[str, Path], level: LogLevel) -> None:
        """
        Instantiate a new logger object.
        """
        self.path = Path(path)
        self.level = level

        self.__logger = getLogger(__name__)
        self.__logger.setLevel(level.value)

    def add_handler(self: Self, target: Optional[Union[str, Path]]=None) -> None:
        """
        Add a file handler to this logger instance. If no `target` is specified,
        log output to console (`stdout`) instead.
        """
        formatter = None
        extension = Path(target).suffix if target is not None else "*"

        match extension:
            case ".log" | ".dat" | ".txt":
                formatter = Formatter(
                    "%(asctime)s [%(levelname)s]::%(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            case ".json":
                raise NotImplementedError()
            case ".csv":
                raise NotImplementedError()
            case _:
                console = StreamHandler(sys.stdout)
                formatter = Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
                console.setFormatter(formatter)
                self.__logger.addHandler(console)
                return

        target.touch(exist_ok=True)
        handler = FileHandler(self.path.joinpath(target))
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

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
