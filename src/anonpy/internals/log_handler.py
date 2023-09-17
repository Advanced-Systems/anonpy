#!/usr/bin/env python3

import csv
import json
import sys
from enum import Enum, unique
from logging import FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Dict, List, Optional, Self, Union

from .csv_formatter import CsvFormatter
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
        self.formatter: Union[Formatter, JsonFormatter, CsvFormatter] = None
        # The file name (including extension) is used as a key
        self.handlers: Dict[str, FileHandler] = {}

        self.__logger = getLogger(__name__)
        self.__logger.setLevel(level.value)

    def set_base_path(self: Self, path: Union[str, Path]) -> Self:
        """
        Set the log file's base path.
        """
        self.path = Path(path)
        return self

    def add_handler(
            self: Self,
            name: Optional[Union[str, Path]]=None,
            layout: Optional[Union[str, Dict[str,str]]]=None
        ) -> Self:
        """
        Add a file handler to this logger instance. If no `name` is specified,
        log output to `stdout` instead.

        Note that plain log files or console logs should define the layout as a `str`.
        """
        target = Path(name).suffix if name is not None else "console"
        default_layout = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        default_structured_layout = {
            "timestamp": "asctime",
            "level": "levelname",
            "name": "name",
            "file": "filename",
            "line": "lineno",
            "message": "message"
        }

        match target:
            case ".log" | ".dat" | ".txt":
                self.formatter = Formatter(default_layout or layout)
            case ".csv":
                self.formatter = CsvFormatter(fmt_dict=layout or default_structured_layout)
            case ".json":
                self.formatter = JsonFormatter(fmt_dict=layout or default_structured_layout)
            case "console":
                console = StreamHandler(sys.stdout)
                self.formatter = Formatter(default_layout or layout)
                console.setFormatter(self.formatter)
                self.__logger.addHandler(console)
                return self
            case _:
                raise NotImplementedError()

        log_file = self.path.joinpath(name)
        log_file.touch(exist_ok=True)
        handler = FileHandler(log_file)
        handler.setFormatter(self.formatter)
        self.handlers[log_file.name] = handler
        self.__logger.addHandler(handler)
        return self

    def get_log_history(
            self: Self,
            name: Union[str, Path]
        ) -> Union[List[str], List[List[str]], List[Dict[str, Any]]]:
        """
        Return the log file content.

        ### Return Types
        - Text: `List[str]`
        - CSV: `List[List[str]]`
        - JSON: `List[Dict[str, Any]]`

        Raise a `FileNotFoundError` if the file doesn't exist.
        Raise a `NotImplementedError` if an unsupported file format is requested.
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
                    lines = ",".join(file_handler.readlines()).replace("\n", "")
                    return json.loads(f"[{lines}]")
                case _:
                    raise NotImplementedError()

    def unlink(self: Self, name: Union[str, Path], missing_ok: bool=False) -> None:
        """
        Remove a log file, located in `self.path`.

        Raise a `FileNotFoundError` if `name` is an invalid log file name.
        """
        file = self.path.joinpath(name)
        handler = self.handlers.get(file.name, None)

        if handler is None or not file.exists():
            raise FileNotFoundError("This log file doesn't exist, or wasn't registered as a handler to this logger")

        # We need to remove and close the handler before unlinking the log file,
        # otherwise it will still be used by the logging process, which in turn
        # would cause an error (e.g. WinError 32) on deletion that results in an
        # application crash
        self.__logger.removeHandler(handler)
        handler.close()
        file.unlink(missing_ok)

    def shutdown(self: Self) -> None:
        """
        Perform any cleanup actions in the logging system (e.g. flushing buffers).

        Should be called at application exit.
        """
        for handler in reversed(self.handlers.values()):
            try:
                handler.acquire()
                handler.flush()
                handler.close()
            except (OSError, ValueError):
                pass
            finally:
                handler.release()

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

        Raise a `TypeError` exception if the logger is configured incorrectly.
        """
        if hide: return
        if not self.handlers: raise TypeError("Logger configured incorrectly: no handler attached this object")

        self.__logger.log(level.value, message, *args)

    def debug(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.DEBUG`.
        """
        self.log(LogLevel.DEBUG, message, *args, hide=hide)

    def info(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.INFO`.
        """
        self.log(LogLevel.INFO, message, *args, hide=hide)

    def warning(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.WARNING`.
        """
        self.log(LogLevel.WARNING, message, *args, hide=hide)

    def error(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.ERROR`.
        """
        self.log(LogLevel.ERROR, message, *args, hide=hide)

    def critical(self: Self, message: str, *args: object, hide: bool=False) -> None:
        """
        Log `message % args` with severity `LogLevel.CRITICAL`.
        """
        self.log(LogLevel.CRITICAL, message, *args, hide=hide)

    #endregion
