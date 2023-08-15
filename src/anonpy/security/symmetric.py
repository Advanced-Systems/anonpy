#!/usr/bin/env python3

import base64
import os
from enum import Enum, unique
from pathlib import Path
from typing import Optional, Self, Union, overload
from warnings import warn

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


@unique
class KDF(Enum):
    PBKDF2HMAC = 1
    Scrypt = 2

class Symmetric:
    """
    Symmetric
    ---------
    High-level class for symmetric encryption and decryption of data.

    ```python
    >>> from pathlib import Path
    >>> from anonpy.security import get_random_password, KDF, Symmetric

    >>> # generate a new key
    >>> sym = Symmetric()
    >>> password = get_random_password(length=32)
    >>> sym.generate_key(password, key_derivation_function=KDF.PBKDF2HMAC)

    >>> # encrypt a message
    >>> cypher = sym.encrypt("Hello, World!")
    >>> print(f"{cypher=}")

    >>> # decrypt the cypher again
    >>> source = sym.decrypt(cypher)
    >>> print(f"{source=})
    ```
    """

    @overload
    def __init__(self: Self) -> None:
        """
        Instantiate a new object suitable for symmetric encryption and decryption.
        """
        ...

    @overload
    def __init__(self: Self, key_storage_path: Union[str, Path]) -> None:
        """
        Instantiate a new object suitable for symmetric encryption and decryption.
        The `key_storage_path` defines a folder for storing symmetric keys persistently
        on disk for later retrieval.

        ### Related methods
        - `store_key`
        - `read_key`
        - `delete_key`
        """
        ...

    def __init__(self: Self, key_storage_path: Optional[Union[str, Path]]=None) -> None:
        self.key_storage_path = None if key_storage_path is None else Path(key_storage_path)
        self.__salt = None
        self.__key = None
        self.__fernet = None

    @overload
    def delete_key(self: Self) -> None:
        """
        Remove all internal attribute references to a previously generated key.
        """
        ...

    @overload
    def delete_key(self: Self, path: Optional[Union[str, Path]]) -> None:
        """
        Remove all internal attribute references to a previously generated key
        and remove the key file located in the key storage path (if any).
        """
        ...

    def delete_key(self: Self, path: Optional[Union[str, Path]]=None) -> None:
        self.__salt = None
        self.__key = None
        self.__fernet = None

        if path is not None:
            Path(self.key_storage_path).joinpath(path).unlink(missing_ok=True)

    @overload
    def generate_key(self: Self) -> None:
        """
        Generate a fresh fernet key.
        """
        ...

    @overload
    def generate_key(
            self: Self,
            password: str,
            encoding: str="utf-8",
            key_derivation_function: KDF=KDF.PBKDF2HMAC
        ) -> None:
        """
        Generate a fresh fernet key. This function will run the password through
        the specified key derivation function.

        PBKDF2 (Password Based Key Derivation Function 2) is typically used for
        deriving a cryptographic key from a password. It may also be used for key
        storage, but an alternate key storage KDF such as `Scrypt` is generally
        considered a better solution.
        """
        ...

    def generate_key(
            self: Self,
            password: Optional[str]=None,
            encoding: str="utf-8",
            key_derivation_function: KDF=KDF.PBKDF2HMAC
        ) -> None:
        if (self.__fernet is not None):
            warn("replacing current fernet token", category=UserWarning, stacklevel=2)

        if (password is None):
            self.__key = Fernet.generate_key()
            self.__fernet = Fernet(self.__key)
            return

        self.__salt = os.urandom(16)
        kdf = None

        match key_derivation_function:
            case KDF.Scrypt:
                kdf = Scrypt(
                    salt=self.__salt,
                    length=32,
                    n=2**14,
                    r=8,
                    p=1,
                    backend=default_backend()
                )
            case _:
                kdf = PBKDF2HMAC(
                    algorithm=SHA256(),
                    length=32,
                    salt=self.__salt,
                    iterations=480_00
                )

        self.__key = base64.urlsafe_b64encode(kdf.derive(password.encode(encoding)))
        self.__fernet = Fernet(self.__key)

    def store_key(self: Self, path: Union[str, Path]) -> None:
        """
        Store symmetric key in the key storage path.

        Raise a `TypeError` exception if the key hasn't been generated yet
        before calling this function.

        ## Remarks
        - symmetric key files should have a `.key` file extension
        """
        if (self.key_storage_path is None):
            raise TypeError("key_storage_path is udefined")
        if (self.__fernet is None):
            raise TypeError("cannot perform this operation without a fernet token")

        self.key_storage_path.joinpath(path).write_bytes(self.__key)

    def read_key(self: Self, path: Union[str, Path]) -> bytes:
        """
        Open the key file in bytes mode and bind its data to this object.
        """
        if (self.__fernet is not None):
            warn("replacing current fernet token", category=UserWarning, stacklevel=2)

        self.__key = self.key_storage_path.joinpath(path).read_bytes()
        self.__fernet = Fernet(self.__key)

    def encrypt(self: Self, data: Union[str, bytes], encoding: str="utf-8") -> bytes:
        """
        Encrypt `data` using a cryptographically secure `Fernet` token.

        Raise a `TypeError` exception if the key hasn't been generated yet
        before calling this function.
        """
        if (self.__fernet is None):
            raise TypeError("cannot perform this operation without a fernet token")

        message = data.encode(encoding) if isinstance(data, str) else data
        return self.__fernet.encrypt(message)

    def decrypt(self: Self, cypher: bytes, encoding: str="utf-8") -> str:
        """
        Decrypt a cypher that was encrypted with a `Fernet` token.
        """
        return self.__fernet.decrypt(cypher).decode(encoding)
