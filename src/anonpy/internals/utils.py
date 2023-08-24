#!/usr/bin/env python3

import functools
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Union

from requests_toolbelt import MultipartEncoderMonitor
from tqdm import tqdm


def deprecate(message: str) -> None:
    """
    Issue a deprecation warning to the calling function.
    """
    warnings.warn(message, category=DeprecationWarning, stacklevel=2)

def ignore_warnings(category: Warning):
    def ignore_warnings_decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=category)
                return func(*args, **kwargs)
        return wrapper
    return ignore_warnings_decorator

def join_url(url: str, *paths) -> str:
    """
    Join a relative list of paths with a URL.
    """
    return functools.reduce(lambda u, p: f"{u}/{p}", [url, *paths])

def unique(iter: Iterable[Any]) -> Iterable[Any]:
    """
    Remove all duplicated entries from a collection.
    """
    return list(dict.fromkeys(iter))

def str2bool(val: str) -> bool:
    """
    Convert a string to boolean.

    Note: This function only supports short and simple English responses to
    yes/no questions.
    """
    return val.lower() in ("yes", "y", "true", "t", "1", "on", "")

def read_file(path: Union[str, Path]) -> Iterator[str]:
    """
    Open a text file and returns its right-striped content line by line, except
    those lines that start with a `#` character (comments).
    """
    with open(path, mode="r", encoding="utf-8") as file_handler:
        yield (line.rstrip() for line in file_handler.readlines() if line[0] != "#")

def _progressbar_options(
        iterable: Iterable,
        desc: str,
        unit: str,
        color: str="\033[32m",
        char: str="\u25CB",
        total: int=None,
        disable: bool=False
    ) -> Dict:
    """
    Return custom optional arguments for `tqdm` progressbars.
    """
    return {
        "iterable": iterable,
        "bar_format": "{l_bar}%s{bar}%s{r_bar}" % (color, "\033[0m"),
        "ascii": char.rjust(9, " "),
        "desc": desc,
        "unit": unit.rjust(1, " "),
        "unit_scale": True,
        "unit_divisor": 1024,
        "total": len(iterable) if total is None else total,
        "disable": not disable
    }

def _callback(monitor: MultipartEncoderMonitor, tqdm_handler: tqdm) -> None:
    """
    Defines a multi-part encoder monitor callback function for progress feedback.
    """
    tqdm_handler.total = monitor.len
    tqdm_handler.update(monitor.bytes_read - tqdm_handler.n)
