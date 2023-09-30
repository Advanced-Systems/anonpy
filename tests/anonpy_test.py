#!/usr/bin/env python3

from pathlib import Path
from typing import Self, Type
from unittest import TestCase
from unittest.mock import MagicMock, patch

from anonpy import AnonPy, Endpoint

from .mocks import MockPixelDrain


class TestAnonPy(TestCase):
    """
    TestAnonPy
    ----------

    In this unit test, we test the `AnonPy` class by example of mocking the
    `PixelDrain` provider.
    """
    @classmethod
    def setUpClass(cls: Type[Self]) -> None:
        cls.api = "https://mock.provider.com/api/"
        cls.endpoint = Endpoint(upload="/file", preview="/file/{}/info", download="/file/{}")
        cls.anon = AnonPy(cls.api, cls.endpoint)

    @classmethod
    def tearDownClass(cls: Type[Self]) -> None:
        del cls.anon

    @patch("anonpy.AnonPy.upload")
    def test_upload(self: Self, mock_upload: MagicMock) -> None:
        # Arrange
        args = {"path": "foo.txt", "progressbar": False}
        mock_upload.return_value = MockPixelDrain.get_upload_response(http_code=200)

        # Act
        upload = mock_upload(**args)

        # Assert
        mock_upload.assert_called_once_with(**args)
        self.assertTrue(upload.get("success", False))

    @patch("anonpy.AnonPy.preview")
    def test_preview(self: Self, mock_preview: MagicMock) -> None:
        # Arrange
        args = {"resource": MockPixelDrain.id}
        mock_preview.return_value = MockPixelDrain.get_preview_response(http_code=200)

        # Act
        preview = mock_preview(**args)

        # Assert
        mock_preview.assert_called_once_with(**args)
        self.assertTrue(preview.get("success", False))
        self.assertEqual(preview.get("downloads", -1), 1)
        self.assertEqual(len(preview.keys()), 24)

    @patch("anonpy.AnonPy.preview")
    def test_preview_with_log_handler(self: Self, mock_preview: MagicMock) -> None:
        # Arrange
        log_file = "test.json"
        args = {"resource": MockPixelDrain.id}

        self.anon.logger \
            .set_base_path(path=Path.home()) \
            .add_handler(log_file)

        mock_preview.side_effect = [self.anon.logger.debug("This shouldn't be logged.", hide=True)]
        mock_preview.return_value = MockPixelDrain.get_preview_response(http_code=200)

        log_path = self.anon.logger.path.joinpath(log_file)

        # Act 1
        mock_preview(**args)
        log_book = self.anon.logger.get_log_history(log_file)
        # Assert 1
        mock_preview.assert_called_once()
        self.assertTrue(log_path.exists())
        self.assertFalse(len(log_book), msg="Expected log file to be empty because logging is disabled")

        # Act 2
        self.anon.enable_logging = True
        mock_preview.side_effect = [self.anon.logger.debug("Hello, %s!", "World")]
        mock_preview(**args)
        log_book = self.anon.logger.get_log_history(log_file)
        # Assert 2
        expected = 2
        self.assertEqual(expected, mock_preview.call_count)
        self.assertTrue(len(log_book), msg="Expected log records in log book because is enabled")

        # Act 3
        self.anon.logger.unlink(log_file)
        # Assert 3
        self.assertFalse(log_path.exists(), msg="Expected log file to be removed on deletion")

    @patch("anonpy.AnonPy.download")
    def test_download(self: Self, mock_download: MagicMock) -> None:
        # Arrange
        args = {"resource": MockPixelDrain.id, "path": Path.home()}
        mock_download.return_value = MockPixelDrain.get_download_response(http_code=200)

        # Act
        download = mock_download(**args)

        # Assert
        mock_download.assert_called_once_with(**args)
        self.assertFalse(download.closed)
        self.assertGreater(len(download.getvalue()), 0)
