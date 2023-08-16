#!/usr/bin/env python3

from pathlib import Path
from typing import Self

import pytest

from anonpy.security import Asymmetric, generate_random_password

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

        # Assert
        assert message == source
        asym.delete_keys()

    @pytest.mark.parametrize("password", [None, generate_random_password(32)])
    def test_encryption_and_decryption_with_file_key(self: Self, password: str) -> None:
        # Arrange
        asym = Asymmetric(key_storage_path=Path.cwd())
        asym.generate_keys()
        message = "Hello, World!"
        private_key = "test-private-key.pem"
        public_key = "test-public-key.pem"

        # Act
        asym.store_private_key(private_key, password)
        asym.store_public_key(public_key)
        asym.delete_keys()
        asym.load_keys(public_key, private_key, password)

        cypher = asym.encrypt(message=message)
        source = asym.decrypt(cypher=cypher)

        # Assert
        assert message == source
        asym.delete_keys(private_key, public_key)

    def test_encryption_and_decryption_on_file(self: Self) -> None:
        # Arrange
        asym = Asymmetric()
        asym.generate_keys()
        message = "Hello, World!"
        document = Path.cwd().joinpath("test.txt")
        document.touch(exist_ok=False)
        document.write_text(message)

        # Act
        asym.encrypt(path=document)
        asym.decrypt(path=document)
        source = document.read_text()

        # Assert
        assert message == source
        asym.delete_keys()
        document.unlink(missing_ok=False)
