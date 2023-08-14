#!/usr/bin/env python3

import binascii
from pathlib import Path
from typing import Self, Union
from warnings import warn

from cryptography.hazmat.primitives.hashes import Hash, HashAlgorithm

from .security_warning import SecurityWarning


class Checksum:
    def __init__(self: Self, path: Union[str, Path], algorithm: HashAlgorithm) -> None:
        self.path = path
        self.algorithm = algorithm()
        self.value = None

    def compute(self: Self) -> None:
        if (self.algorithm.name in ("md5", "sha1")):
            warn(f"{self.algorithm.name.upper()} is an insecure hashing algorithm", SecurityWarning, stacklevel=2)

        digest = Hash(self.algorithm)

        with open(self.path, mode="rb") as file_handler:
            bytes = file_handler.read()
            digest.update(bytes)

        self.value = digest.finalize()

    def __str__(self: Self) -> str:
        return binascii.b2a_hex(self.value).decode() if self.value is not None else "unhashed"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path},algorithm={self.algorithm.name},hash={str(self)})"
