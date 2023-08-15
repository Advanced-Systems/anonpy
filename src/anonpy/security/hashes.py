#!/usr/bin/env python3

import binascii
from pathlib import Path
from typing import Self, Union
from warnings import warn

from cryptography.hazmat.primitives.hashes import Hash, HashAlgorithm

from .security_warning import SecurityWarning


class Checksum:
    """
    Checksum
    --------

    The `Checksum` class implements commonly used hashing functions for checking
    the integrity of a file, and uses the `cryptography.hazmat.primitives.hashes`
    namespace internally for this purpose.

    ```python
    >>> from anonpy.security import Checksum, SHA256
    >>> checksum = Checksum("notes.txt", SHA256)
    >>> checksum.compute()
    >>> # convert the hash digest (bytes) to string
    >>> sha256_hash = str(checksum)
    >>> print(sha256_hash)
    '12998c017066eb0d2a70b94e6ed3192985855ce390f321bbdb832022888bd251'
    ```
    """
    def __init__(self: Self, path: Union[str, Path], algorithm: HashAlgorithm) -> None:
        self.path = path
        self.algorithm = algorithm()
        self.hash = None

    def compute(self: Self) -> None:
        """
        Computes the hash digest as bytes and stores the result in the `hash`
        property of the current object.
        """
        if (self.algorithm.name in ("md5", "sha1")):
            warn(f"{self.algorithm.name.upper()} is an insecure hashing algorithm", SecurityWarning, stacklevel=2)

        digest = Hash(self.algorithm)

        with open(self.path, mode="rb") as file_handler:
            bytes_ = file_handler.read()
            digest.update(bytes_)

        self.hash = digest.finalize()

    def __str__(self: Self) -> str:
        return binascii.b2a_hex(self.hash).decode() if self.hash is not None else "unhashed"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path},algorithm={self.algorithm.name},hash={str(self)})"
