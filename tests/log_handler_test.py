#!/usr/bin/env python3

from pathlib import Path
from typing import Self, Type
from unittest import TestCase

from anonpy.internals import LogHandler, LogLevel


class TestLogHandler(TestCase):
    """
    TestLogHandler
    --------------

    Perform simple behavior tests in order to confirm that log files are created,
    and their records contain the messages to be logged; the custom formatter classes
    are the main test subjects here.
    """
    @classmethod
    def setUpClass(cls: Type[Self]) -> None:
        cls.logger = LogHandler(path=Path.home(), level=LogLevel.DEBUG)
        cls.text_log = "text_log.log"
        cls.csv_log = "csv_log.csv"
        cls.json_log = "json_log.json"

    @classmethod
    def tearDownClass(cls: Type[Self]) -> None:
        cls.logger.unlink(cls.text_log)
        cls.logger.unlink(cls.csv_log)
        cls.logger.unlink(cls.json_log)

    def test_text_formatter(self: Self) -> None:
        # Arrange
        args = ["World"]
        self.logger.add_handler(self.text_log)

        # Act
        self.logger.debug("Hello, %s", *args)
        log_book = self.logger.get_log_history(self.text_log)
        record = log_book.pop()

        # Assert
        self.assertTrue(self.logger.path.joinpath(self.text_log).exists())
        self.assertTrue(args.pop() in record)

    def test_csv_formatter(self: Self) -> None:
        # Arrange
        args = ["World"]
        self.logger.add_handler(self.csv_log)

        # Act
        self.logger.debug("Hello, %s", *args)
        log_book = self.logger.get_log_history(self.csv_log)
        record = log_book[0]

        # Assert
        self.assertTrue(self.logger.path.joinpath(self.csv_log).exists())
        self.assertTrue(args.pop() in record[-1])

    def test_json_formatter(self: Self) -> None:
        # Arrange
        args = ["World"]
        layout = {"file": "filename", "message": "message"}
        self.logger.add_handler(self.json_log, layout=layout)

        # Act
        self.logger.debug("Hello, %s", *args)
        log_book = self.logger.get_log_history(self.json_log)
        record = log_book.pop()

        # Assert
        self.assertTrue(self.logger.path.joinpath(self.json_log).exists())
        self.assertTrue(args.pop() in record.get("message", "n/a"))
        self.assertFalse(record.get("level", False))
