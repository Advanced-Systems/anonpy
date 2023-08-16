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
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"

        # Act
        cypher = sym.encrypt(message=message)
        source = sym.decrypt(cypher=cypher)

        # Assert
        assert message == source
        sym.delete_key()

    def test_encryption_and_decryption_with_key_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric(key_storage_path=Path.home())
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"
        sym_key = "test.key"

        # Act
        sym.store_key(sym_key)
        sym.delete_key()
        sym.load_key(sym_key)

        cypher = sym.encrypt(message=message)
        source = sym.decrypt(cypher=cypher)

        # Assert
        assert message == source
        sym.delete_key(sym_key)

    def test_encryption_on_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric()
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"
        document = Path.cwd().joinpath("test.txt")
        document.touch(exist_ok=False)
        document.write_text(message)

        # Act
        sym.encrypt(path=document)
        sym.decrypt(path=document)
        source = document.read_text()

        # Assert
        assert message == source
        sym.delete_key()
        document.unlink(missing_ok=False)
