#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Self
from uuid import uuid4

import pytest

from anonpy.security import KDF, Symmetric


@pytest.mark.parametrize("password", sorted(["", "2geY6OSahqDRk/AXcYWxsvCL3eGx9laN2hu4j7A2pYI="]))
@pytest.mark.parametrize("kdf", [KDF.PBKDF2HMAC, KDF.Scrypt])
class TestSymmetric:
    def test_encryption_and_decryption(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric()
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"

        # Act
        cipher = sym.encrypt(message=message)
        source = sym.decrypt(cipher=cipher)
        sym.delete_key()

        # Assert
        assert message == source

    def test_encryption_and_decryption_with_key_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric(key_storage_path=Path.home())
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"
        sym_key = f"test_{uuid4()}.key"

        try:
            # Act
            sym.store_key(sym_key)
            sym.delete_key()
            sym.load_key(sym_key)
            cipher = sym.encrypt(message=message)
            source = sym.decrypt(cipher=cipher)
            # Assert
            assert message == source
        except ValueError as error:
            print(error.with_traceback(), file=sys.stderr)
        finally:
            sym.delete_key(sym_key)

    def test_encryption_on_file(self: Self, password: str, kdf: KDF) -> None:
        # Arrange
        sym = Symmetric()
        sym.generate_key(password, key_derivation_function=kdf)
        message = "Hello, World!"
        document = Path.cwd().joinpath(f"test_symmetric_{uuid4()}.txt")
        document.touch(exist_ok=True)
        document.write_text(message)

        try:
            # Act
            sym.encrypt(path=document)
            sym.decrypt(path=document)
            source = document.read_text()
            # Assert
            assert message == source
        except ValueError as error:
            print(error.with_traceback(), file=sys.stderr)
        finally:
            sym.delete_key()
            document.unlink(missing_ok=True)
