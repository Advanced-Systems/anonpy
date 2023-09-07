#!/usr/bin/env python3

from typing import Self

from anonpy.security import Checksum, MD5, SecurityWarning
from anonpy.internals import ignore_warnings

class TestHashes:
    @ignore_warnings(category=SecurityWarning)
    def test_md5_hash(self: Self) -> None:
        # Arrange
        data = "Hello, World!"

        # Act
        md5_hash = Checksum.compute(data=data, algorithm=MD5)
        checksum = Checksum.hash2string(md5_hash)

        # Assert
        expected = "65a8e27d8879283831b664bd8b7f0ad4"
        assert checksum == expected
