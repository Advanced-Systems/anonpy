#!/usr/bin/env python3

import ast
import difflib
import functools
import os
import platform
import subprocess
import textwrap
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Union

from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn

console = Console(color_system="256")

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
    return functools.reduce(lambda u, p: f"{u.rstrip("/")}/{p.lstrip("/")}", [url, *paths])

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

def truncate(text: str, width: int, placeholder: str="...") -> str:
    """
    Reduce the given text with a placeholder to fit in the given width.
    """
    stripped = text.strip()
    if len(stripped) <= width: return stripped

    return textwrap.shorten(stripped, width, placeholder=placeholder)

def read_file(path: Union[str, Path]) -> Iterator[str]:
    """
    Open a text file and returns its right-striped content line by line, except
    those lines that start with a `#` character (comments).
    """
    with open(path, mode="r", encoding="utf-8") as file_handler:
        yield (line.rstrip() for line in file_handler.readlines() if line[0] != "#")

def print_diff(a: str, b: str, console: Console) -> None:
    """
    Print difference between two strings to `console`.
    """
    diff = difflib.ndiff(
        f"{a}\n".splitlines(keepends=True),
        f"{b}\n".splitlines(keepends=True)
    )

    console.print("".join(diff), end="")

def copy_to_clipboard(text: str) -> None:
    """
    Copy the passed text to clipboard.
    """
    subprocess.run("clip", input=text, check=True, encoding="utf-8")

def get_progress_bar() -> Progress:
    """
    Return a `rich` progress bar. This configuration expects a `name` property
    to be initialized with the `add_task` method.
    """
    return Progress(
        TextColumn("[bold blue]{task.fields[name]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )
