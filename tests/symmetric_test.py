#!/usr/bin/env python3

from pathlib import Path
from typing import Self

import pytest

from anonpy.security import KDF, Symmetric, generate_random_password


@pytest.mark.parametrize("password", [None, generate_random_password(32)])
@pytest.mark.parametrize("kdf", [KDF.PBKDF2HMAC, KDF.Scrypt])
class TestSymmetric:
    def test_encryption_and_decryption(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric()
        message = "Hello, World!"

        # Act
        sym.generate_key(password, key_derivation_function=kdf)
        cypher = sym.encrypt(message=message)
        source = sym.decrypt(cypher=cypher)

        # Assert
        assert message == source
        sym.delete_key()

    def test_encryption_and_decryption_with_key_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric(key_storage_path=Path.home())
        message = "Hello, World!"
        file = "test.key"

        # Act
        sym.generate_key(password, key_derivation_function=kdf)
        sym.store_key(file)
        sym.delete_key()
        sym.load_key(file)

        cypher = sym.encrypt(message=message)
        source = sym.decrypt(cypher=cypher)

        # Assert
        assert message == source
        sym.delete_key(file)

    def test_encryption_on_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric(key_storage_path=Path.cwd())
        message = "Hello, World!"
        file = sym.key_storage_path.joinpath("test.txt")
        file.touch(exist_ok=False)
        file.write_text(message)

        # Act
        sym.generate_key(password, key_derivation_function=kdf)
        sym.encrypt(path=file)
        sym.decrypt(path=file)
        source = file.read_text()

        # Assert
        assert message == source
        sym.delete_key()
        file.unlink()
