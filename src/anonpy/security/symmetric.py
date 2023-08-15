#!/usr/bin/env python3

import base64
import os
from pathlib import Path
from typing import Optional, Self, Union
from warnings import warn

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC, KeyDerivationFunction


class Symmetric:
    """
    Symmetric
    ---------
    High-level class for symmetric encryption and decryption of data.

    ```python
    >>> from pathlib import Path
    >>> from anonpy.security import Symmetric, PBKDF2HMAC

    >>> # generate a new key
    >>> sym = Symmetric(key_storage_path=Path.home())
    >>> sym.generate_key()

    >>> # encrypt a message
    >>> cypher = sym.encrypt("Hello, World!")
    >>> print(f"{cypher=}")

    >>> # decrypt the cypher again
    >>> source = sym.decrypt(cypher)
    >>> print(f"{source=})
    ```
    """
    def __init__(
        self: Self,
        key_storage_path: Union[str, Path],
        password: Optional[str]=None
    ) -> None:
        """
        Instantiate a new object suitable for symmetric encryption and decryption.
        The `key_storage_path` defines a folder for storing `*.key` files. Symmetric
        keys can be generated with or without a password.
        """
        self.key_storage_path = Path(key_storage_path)
        self.password = password
        self.__salt = None
        self.__key = None
        self.__fernet = None

    def __del__(self: Self) -> None:
        self.password = None
        self.__salt = None
        self.__key = None
        self.__fernet = None

    def generate_key(self: Self, key_derivation_function: KeyDerivationFunction=PBKDF2HMAC) -> None:
        """
        Generate a fresh fernet key. If a password was set through the contructor,
        this function will run the password through the key derivation function.

        PBKDF2 (Password Based Key Derivation Function 2) is typically used for
        deriving a cryptographic key from a password. It may also be used for key
        storage, but an alternate key storage KDF such as `Scrypt` is generally
        considered a better solution.
        """
        if (self.password is None):
            self.__fernet = Fernet.generate_key()
            return

        if (self.__key is not None):
            warn("replacing current key", category=UserWarning, stacklevel=2)

        self.__salt = os.urandom(16)
        kdf = key_derivation_function(
            algorithm=SHA256(),
            length=32,
            salt=self.__salt,
            iterations=480_000
        )

        self.__key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.__fernet = Fernet(self.__key)

    def store_key(self: Self, path: Union[str, Path]) -> None:
        """
        Store the `<path>.key` file in the key storage path.

        Raise a `TypeError` exception if the key hasn't been generated yet
        before calling this function.
        """
        if (self.__key is None):
            raise TypeError("key hasn't been generated yet")

        self.key_storage_path.joinpath(path).write_bytes(self.__key)

    def read_key(self: Self, path: Union[str, Path]) -> bytes:
        """
        Open the key file in bytes mode and return its content.
        """
        return self.key_storage_path.joinpath(path).read_bytes()

    def encrypt(self: Self, data: Union[str, bytes], encoding: str="utf-8") -> bytes:
        """
        Encrypt `data` using a cryptographically secure `Fernet` token.

        Raise a `TypeError` exception if the key hasn't been generated yet
        before calling this function.
        """
        if (self.__key is None):
            raise TypeError("key hasn't been generated yet")

        message = data.encode(encoding) if isinstance(data, str) else data
        return self.__fernet.encrypt(message)

    def decrypt(self: Self, cypher: bytes, encoding: str="utf-8") -> str:
        """
        Decrypt a cypher that was encrypted with a `Fernet` token.
        """
        return self.__fernet.decrypt(cypher).decode(encoding)

