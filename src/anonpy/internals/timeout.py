#!/usr/bin/env python3

from typing import Optional, Self, Union, overload
from warnings import warn


class Timeout:
    """
    Timeout
    -------
    You can tell Requests to stop waiting for a response after a given number of
    seconds with the timeout parameter. Nearly all production code should use this
    parameter in nearly all requests. A `Timeout` controls the maximum amount of
    time that can pass before the underlying socket receives any data.

    Issue a `UserWarning` if timeout is instantiated with `None`.

    ### Note
    In the event of a network problem (e.g. DNS failure, refused connection, etc),
    Requests will raise a `ConnectionError` exception.
    """
    __slots__ = [
        "values",
        "connect",
        "read"
    ]

    @overload
    def __init__(self: Self, values: Union[int, float]) -> None:
        """
        Create a new `Timeout` object with equal values for `connect` and `read`.
        """
        ...

    @overload
    def __init__(self: Self, connect: Union[int, float], read: Union[int, float]) -> None:
        """
        Create a new `Timeout` object with separate values for `connect` and `read`.
        """
        ...

    def __init__(
            self: Self,
            values: Optional[Union[int, float]]=None,
            connect: Optional[Union[int, float]]=None,
            read: Optional[Union[int, float]]=None
        ) -> None:
        self.values = values or (connect, read)
        self.connect = values or connect
        self.read = values or read

        if values is None and connect is None and read is None:
            warn(
                message="Not specifying a timeout may cause your program to hang indefinitely",
                category=UserWarning,
                stacklevel=2
            )
