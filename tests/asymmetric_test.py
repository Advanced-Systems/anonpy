#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Self

import pytest

from anonpy.security import Asymmetric

class TestAsymmetric:
    def test_encryption_and_decryption(self: Self) -> Self:
        # Arrange
        asym = Asymmetric()
        asym.generate_private_key()
        asym.generate_public_key()
        message = "Hello, World!"

        # Act
        cypher = asym.encrypt(message=message)
        source = asym.decrypt(cypher=cypher)
        asym.delete_keys()

        # Assert
        assert message == source

    @pytest.mark.parametrize("password", sorted(["", "Di3GQNwpurf5ymbgs/bubCOrWpAwNe+0arsdoakmlzo="]))
    def test_encryption_and_decryption_with_file_key(self: Self, password: str) -> None:
        # Arrange
        asym = Asymmetric(key_storage_path=Path.cwd())
        asym.generate_keys()
        message = "Hello, World!"
        private_key = f"test_private_key_{len(password)}.pem"
        public_key = f"test_public_key_{len(password)}.pem"

        # Act
        asym.store_private_key(private_key, password)
        asym.store_public_key(public_key)
        asym.delete_keys()
        asym.load_keys(public_key, private_key, password)

        cypher = asym.encrypt(message=message)
        source = asym.decrypt(cypher=cypher)
        asym.delete_keys(private_key, public_key)

        # Assert
        assert message == source

    def test_encryption_and_decryption_on_file(self: Self) -> None:
        # Arrange
        asym = Asymmetric()
        asym.generate_keys()
        message = "Hello, World!"
        document = Path.cwd().joinpath("test_asymmetric.txt")
        document.touch(exist_ok=True)
        document.write_text(message)

        # Act
        try:
            asym.encrypt(path=document)
            asym.decrypt(path=document)
            source = document.read_text()
        except ValueError as error:
            print(error.with_traceback(), file=sys.stderr)
        finally:
            asym.delete_keys()
            document.unlink(missing_ok=True)

        # Assert
        assert message == source
