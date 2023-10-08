#!/usr/bin/env python3

from pathlib import Path
from typing import Self, Type
from unittest import TestCase
from uuid import uuid4

from anonpy.internals import ConfigHandler

class ConfigHandlerTest(TestCase):
    """
    ConfigHandlerTest
    -----------------

    This test class ensures that writing to and reading from INI files works
    as expected.
    """

    @classmethod
    def setUpClass(cls: Type[Self]) -> None:
        cls.cfg_file = Path.home() / f"cfg_file_{uuid4()}.ini"

    @classmethod
    def tearDownClass(cls: Type[Self]) -> None:
        cls.cfg_file.unlink(missing_ok=True)

    def test_basic_config_handler(self: Self) -> None:
        # Arrange
        config = ConfigHandler()

        # Act
        config.add_section("test", settings={
            "hello": "world",
            "number": 1,
            "verbose": True
        })

        config.add_section("config")
        config.set_option("test", "verbose", False)

        # Assert
        self.assertEqual(2, len(config.get_sections()))
        self.assertEqual(3, len(config.get_options("test")))
        self.assertFalse(config.get_option("test", "verbose"))

    def test_file_config_handler(self: Self) -> None:
        # Arrange
        with ConfigHandler(self.cfg_file) as config_handler:
            config_handler.add_section("test", settings={
                "hello": "world",
                "number": 1,
                "verbose": True
            })

        # Act 1
        config = ConfigHandler(self.cfg_file)
        config.read()
        config.path.unlink(missing_ok=False)
        # Assert 1
        self.assertFalse(config.path.exists())
        self.assertTrue(config.get_option("test", "verbose"))

        # Act 2
        data = config.json
        config.save()
        # Assert 2
        self.assertTrue(config.path.exists())
        self.assertEqual(3, len(data["test"].keys()))

        # Act 3
        config.remove_section("test")
        # Assert 3
        self.assertFalse(config.json.get("test", False))
