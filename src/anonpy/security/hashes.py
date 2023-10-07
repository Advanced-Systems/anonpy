#!/usr/bin/env python3

import binascii
from pathlib import Path
from typing import Optional, Self, Type, Union, overload
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

    >>> sha256_hash = Checksum.compute("notes.txt", SHA256)

    >>> # convert the hash digest (bytes) to string
    >>> print(Checksum.hash2string(sha256_hash))
    '12998c017066eb0d2a70b94e6ed3192985855ce390f321bbdb832022888bd251'
    ```
    """
    insecure_hash_algorithms = ["md5", "sha1"]

    @overload
    @classmethod
    def compute(cls: Type[Self], path: Union[str, Path], algorithm: HashAlgorithm, encoding: str="utf-8") -> bytes:
        """
        Compute the checksum of a file using the specified `algorithm`.

        Issue a `SecurityWarning` if the `algorithm` is deemed insecure.

        ### Remark
        You can use the `ignore_warnings` decorator from the `anonpy.internals`
        namespace to ignore `SecurityWarning` issued by this function.
        """
        ...

    @overload
    @classmethod
    def compute(cls: Type[Self], data: str, algorithm: HashAlgorithm, encoding: str="utf-8") -> bytes:
        """
        Compute the checksum of a string using the specified `algorithm`.

        Issue a `SecurityWarning` if the `algorithm` is deemed insecure.

        ### Remark
        You can use the `ignore_warnings` decorator from the `anonpy.internals`
        namespace to ignore `SecurityWarning` issued by this function.
        """
        ...

    @classmethod
    def compute(
            cls: Type[Self],
            algorithm: HashAlgorithm,
            path: Optional[Union[str, Path]]=None,
            data: Optional[str]=None,
            encoding: str="utf-8"
        ) -> bytes:
        if (algorithm.name in cls.insecure_hash_algorithms):
            warn(f"{algorithm.name.upper()} is an insecure hashing algorithm", SecurityWarning, stacklevel=2)

        digest = Hash(algorithm())

        if path is None:
            digest.update(data.encode(encoding))
            return digest.finalize()

        with open(path, mode="rb") as file_handler:
            bytes_ = file_handler.read()
            digest.update(bytes_)

        return digest.finalize()

    @staticmethod
    def hash2string(digest: bytes, encoding: str="utf-8") -> str:
        """
        Convert the hash digest to string.
        """
        return binascii.b2a_hex(digest).decode(encoding)
