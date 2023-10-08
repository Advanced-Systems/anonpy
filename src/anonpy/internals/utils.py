#!/usr/bin/env python3

import ast
import functools
import os
import platform
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Union


def convert(value: str) -> Optional[Any]:
    """
    This method will attempt to deduce a Python literal structures and returns a
    `str` on failing to do so.
    """
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

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

def get_resource_path(package_name: str) -> Path:
    """
    Return a platform-specific resource directory for storing globally
    accessible package files.
    """
    parent = None

    match platform.system():
        case "Windows":
            parent = Path(os.path.expandvars("%LOCALAPPDATA%"))
        case "Darwin":
            parent = Path.home().joinpath("Library").joinpath("Application Support")
        case _:
            # Assume Unix-like file system
            parent = Path.home().joinpath(".config")

    resource_path = parent.joinpath(package_name)
    os.makedirs(resource_path, exist_ok=True)
    return resource_path

def join_url(url: str, *paths) -> str:
    """
    Join a relative list of paths with a URL.
    """
    return functools.reduce(lambda u, p: f"{u}/{p}", [url, *paths])

def get_while(dict_: Dict, default: Any, *keys: str) -> Any:
    """
    Return the value of the first matching key of `dict_`, else `default`.
    """
    for key in keys:
        if (value := dict_.get(key)) is not None:
            return value

    return default

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
