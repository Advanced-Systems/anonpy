#!/usr/bin/env python3

from pathlib import Path
from typing import Optional, Self, Union, overload

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, Encoding, NoEncryption, PrivateFormat, PublicFormat


class Asymmetric:
    """
    Asymmetric
    ----------
    High-level class for asymmetric encryption and decryption.

    ```python
    >>> from pathlib import Path
    >>> from anonpy.security import Asymmetric

    >>> # generate a private-public key pair
    >>> asym = Asymmetric()
    >>> asym.generate_keys()

    >>> # encrypt a message
    >>> cipher = asym.encrypt(message="Hello, World!")
    >>> print(f"{cipher=}")

    >>> # decrypt the cipher again
    >>> source = asym.decrypt(cipher=cipher)
    >>> print(f"{source=}")
    ```
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
        - `store_public_key`
        - `store_private_key`
        - `load_public_key`
        - `load_private_key`
        - `delete_keys`
        """
        ...

    def __init__(self: Self, key_storage_path: Optional[Union[str, Path]]=None) -> None:
        self.key_storage_path = None if key_storage_path is None else Path(key_storage_path)
        self.__private_key = None
        self.__private_pem = None
        self.__public_key = None
        self.__public_pem = None

    @overload
    def delete_keys(self: Self) -> None:
        """
        Remove all internal attribute references to previously generated public-
        private key pairs.
        """
        ...

    @overload
    def delete_keys(self: Self, *paths: Union[str, Path]) -> None:
        """
        Remove all internal attribute references to previously generated public-
        private key pairs and remove the key files located in the key storage path.

        Raise a `TypeError` exception if the `key_storage_path` is undefined.
        """
        ...

    def delete_keys(self: Self, *paths: Optional[Union[str, Path]]) -> None:
        self.__private_key = None
        self.__private_pem = None
        self.__public_key = None
        self.__public_pem = None

        if self.key_storage_path is None and len(paths) > 0:
            raise TypeError("key storage path is undefined")

        for key in filter(None, paths):
            self.key_storage_path.joinpath(key).unlink(missing_ok=True)

    def generate_private_key(self: Self) -> None:
        """
        Generates a new RSA private key.
        """
        self.__private_key = rsa.generate_private_key(
            public_exponent=65_537,
            key_size=2048,
            backend=default_backend()
        )

    def generate_public_key(self: Self) -> None:
        """
        Generates a new RSA public key.

        Raise a `TypeError` exception if a private key hasn't been generated yet.
        """
        if (self.__private_key is None):
            raise TypeError("unable to generate a public key without a private key")

        self.__public_key = self.__private_key.public_key()

    def generate_keys(self: Self) -> None:
        """
        Generates a new RSA private-public key pair.
        """
        self.generate_private_key()
        self.generate_public_key()

    def store_public_key(self: Self, name: str) -> None:
        """
        Store the generated RSA public key to disk, located in the key storage path.
        """
        if (self.key_storage_path is None):
            raise TypeError("key storage path is undefined")

        if (self.__public_key is None):
            raise TypeError("public key not initialized")

        self.__public_pem = self.__public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

        self.key_storage_path.joinpath(name).write_bytes(self.__public_pem)

    @overload
    def store_private_key(self: Self, name: str) -> None:
        """
        Store the generated RSA private key to disk, located in the key storage path.
        """
        ...

    @overload
    def store_private_key(
        self: Self,
        name: str,
        password: str,
        encoding: str="utf-8"
    ) -> None:
        """
        Store the generated RSA private key password-protected to disk, located
        in the key storage path.
        """
        ...

    def store_private_key(
            self: Self,
            name: str,
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        if (self.key_storage_path is None):
            raise TypeError("key storage path is undefined")

        if (self.__private_key is None):
            raise TypeError("private key not initialized")

        encryption_algorithm = (
            NoEncryption() if not password
            else BestAvailableEncryption(password.encode(encoding))
        )

        self.__private_pem = self.__private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

        self.key_storage_path.joinpath(name).write_bytes(self.__private_pem)

    @overload
    def load_private_key(self: Self, name: str) -> None:
        """
        Open the RSA private key file in bytes mode and bind its data to this object.
        """
        ...

    @overload
    def load_private_key(
        self: Self,
        name: str,
        password: str,
        encoding: str="utf-8"
    ) -> None:
        """
        Open the password-protected RSA private key file in bytes mode and bind
        its data to this object.
        """
        ...

    def load_private_key(
            self: Self,
            name: str,
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        raw_bytes = self.key_storage_path.joinpath(name).read_bytes()
        self.__private_key = serialization.load_pem_private_key(
            raw_bytes,
            password=password.encode(encoding) if password else None,
            backend=default_backend()
        )

    def load_public_key(self: Self, name: str) -> None:
        """
        Open the RSA public key file in bytes mode and bind its data to this object.
        """
        raw_bytes = self.key_storage_path.joinpath(name).read_bytes()
        self.__public_key = serialization.load_pem_public_key(raw_bytes, backend=default_backend())

    def load_keys(
            self: Self,
            public_key: str,
            private_key: str,
            password: Optional[str]=None,
            encoding: str="utf-8"
        ) -> None:
        """
        Open the (possibly password protected) RSA private-public key files in bytes
        mode and bind its data to this object.
        """
        self.load_private_key(private_key, password, encoding)
        self.load_public_key(public_key)

    @overload
    def encrypt(self: Self, path: Union[str, Path], encoding: str="utf-8") -> None:
        """
        Encrypt the file located in `path` using the cryptographically secure RSA
        cryptosystem and overwrite its content with the cipher text.

        Raise a `TypeError` exception if the public key hasn't been generated yet.

        ### Remarks
        This function requires keyword arguments.
        """
        ...

    @overload
    def encrypt(self: Self, message: str, encoding: str="utf-8") -> bytes:
        """
        Encrypt the file located in `path` using the cryptographically secure RSA
        cryptosystem and return the cipher.

        Raise a `TypeError` exception if the public key hasn't been generated yet.

        ### Remarks
        This function requires keyword arguments.
        """
        ...

    def encrypt(
            self: Self,
            path: Optional[Union[str, Path]]=None,
            message: Optional[str]=None,
            encoding: str="utf-8"
        ) -> Optional[bytes]:
        if self.__public_key is None:
            raise TypeError("cannot perform this operation without a public key")

        if path is not None and message is not None:
            raise TypeError("illegal combinations of arguments (supplied both path and message)")

        sha256 = SHA256()
        oaep = OAEP(mgf=MGF1(sha256), algorithm=sha256, label=None)

        if path is None:
            data = message.encode(encoding)
            return self.__public_key.encrypt(data, oaep)

        # replace file content with cipher
        file = Path(path)
        source = file.read_bytes()
        cipher = self.__public_key.encrypt(source, oaep)
        file.write_bytes(cipher)

    @overload
    def decrypt(self: Self, path: Union[str, Path], encoding: str="utf-8") -> None:
        """
        Decrypt a file in `path` and replace its content with the decrypted data.

        Raise a `TypeError` exception if the private key hasn't been generated yet.

        ### Remarks
        This function requires keyword arguments.
        """
        ...

    @overload
    def decrypt(self: Self, cipher: bytes, encoding: str="utf-8") -> str:
        """
        Decrypt a cipher that was encrypted with a RSA cryptosystem.

        Raise a `TypeError` exception if the private key hasn't been generated yet.

        ### Remarks
        This function requires keyword arguments.
        """
        ...

    def decrypt(
            self: Self,
            path: Optional[Union[str, Path]]=None,
            cipher: Optional[bytes]=None,
            encoding: str="utf-8"
        ) -> Optional[str]:
        if self.__private_key is None:
            raise TypeError("cannot perform this operation without a private key")

        if path is not None and cipher is not None:
            raise TypeError("illegal combinations of arguments (supplied both path and cipher)")

        sha256 = SHA256()
        oaep = OAEP(mgf=MGF1(sha256), algorithm=sha256, label=None)

        if path is None:
            return self.__private_key.decrypt(cipher, oaep).decode(encoding)

        # restore file from cipher
        file = Path(path)
        cipher = file.read_bytes()
        source = self.__private_key.decrypt(cipher, oaep).decode(encoding)
        file.write_text(source)
