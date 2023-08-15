#!/usr/bin/env python3

from pathlib import Path
from typing import Optional, Self, Union, overload

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, Encoding, NoEncryption, PrivateFormat, PublicFormat


class Asymmetric:
    """
    TODO: documentation
    """

    @overload
    def __init__(self: Self) -> None:
        """
        Instantiate a new object suitable for asymmetric encryption and decryption.
        """
        ...

    @overload
    def __init__(self: Self, key_storage_path: Union[str, Path]) -> None:
        """
        Instantiate a new object suitable for asymmetric encryption and decryption.
        The `key_storage_path` defines a folder for storing public and private keys
        persistently on disk for later retrieval.

        ### Related methods
        - `store_keys`
        - `read_keys`
        - `delete_keys`
        """
        ...

    def __init__(self: Self, key_storage_path: Optional[Union[str, Path]]=None) -> None:
        self.key_storage_path = None if key_storage_path is None else Path(key_storage_path)
        self.__private_key = None
        self.__public_key = None

    @overload
    def delete_key(self: Self) -> None:
        """
        TODO: documentation
        """
        ...

    @overload
    def delete_key(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        ...

    def delete_key(self: Self, path: Optional[Union[str, Path]]=None) -> None:
        raise NotImplementedError()

    def generate_private_key(self: Self) -> None:
        """
        TODO: documentation
        """
        self.__private_key = rsa.generate_private_key(
            public_exponent=65_537,
            key_size=2048,
            backend=default_backend()
        )

    def generate_public_key(self: Self) -> None:
        """
        TODO: documentation
        """
        if (self.__private_key is None):
            raise TypeError("unable to generate a public key without a private key")

        self.__public_key = self.__private_key.public_key()

    def generate_keys(self: Self) -> None:
        """
        TODO: documentation
        """
        self.generate_private_key()
        self.generate_public_key()

    def store_public_key(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        if (self.key_storage_path is None):
            raise TypeError("key storage path is undefined")

        if (self.__public_key is None):
            raise TypeError("public key not initialized")

        pem = self.__public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

        self.key_storage_path.joinpath(path).write_bytes(pem)

    @overload
    def store_private_key(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        ...

    @overload
    def store_private_key(
        self: Self,
        path: Union[str, Path],
        password: str,
        encoding: str="utf-8"
    ) -> None:
        """
        TODO: documentation
        """
        ...

    def store_private_key(
            self: Self,
            path: Union[str, Path],
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        if (self.key_storage_path is None):
            raise TypeError("key storage path is undefined")

        if (self.__private_key is None):
            raise TypeError("private key not initialized")

        encryption_algorithm = (
            NoEncryption() if password is None
            else BestAvailableEncryption(password.encode(encoding))
        )

        pem = self.__private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

        self.key_storage_path.joinpath(path).write_bytes(pem)

    @overload
    def store_keys(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        ...

    @overload
    def store_keys(
        self: Self,
        path: Union[str, Path],
        password: str,
        encoding: str="utf-8"
    ) -> None:
        """
        TODO: documentation
        """
        ...

    def store_keys(
            self: Self,
            path: Union[str, Path],
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        base = Path(path).stem
        self.store_public_key(f"{base}-public-key.pem")
        self.store_private_key(f"{base}-private-key.pem", password, encoding)


    @overload
    def read_private_key(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        ...

    @overload
    def read_private_key(
            self: Self,
            path: Union[str, Path],
            password: str,
            encoding: str="utf-8"
        ) -> None:
        """
        TODO: documentation
        """
        ...

    def read_private_key(
            self: Self,
            path: Union[str, Path],
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        raise NotImplementedError()

    def read_public_key(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        raise NotImplementedError()

    @overload
    def read_keys(self: Self, path: Union[str, Path]) -> None:
        """
        TODO: documentation
        """
        ...

    @overload
    def read_keys(
            self: Self,
            path: Union[str, Path],
            password: str,
            encoding: str="utf-8"
        ) -> None:
        """
        TODO: documentation
        """
        ...

    def read_keys(self: Self, path: Union[str, Path]) -> None:
        raise NotImplementedError()

    def encrypt(self: Self, data: Union[str, bytes], encoding: str="utf-8") -> bytes:
        """
        TODO: documentation
        """
        raise NotImplementedError()

    def decrypt(self: Self, cypher: bytes, encoding: str="utf-8") -> str:
        """
        TODO: documentation
        """
        raise NotImplementedError()
