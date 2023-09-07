#!/usr/bin/env python3

from pathlib import Path
from typing import Self, Type
from unittest import TestCase
from unittest.mock import MagicMock, patch

from anonpy import AnonPy, Endpoint

from .mocks import MockPixelDrain


class TestAnonPy(TestCase):
    """
    Test Scenario
    -------------

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
        self.anon.upload = mock_upload
        self.anon.upload.return_value = MockPixelDrain.get_upload_response(http_code=200)

        # Act
        upload = self.anon.upload(**args)

        # Assert
        self.anon.upload.assert_called_once_with(**args)
        self.assertTrue(upload.get("success", False))

    @patch("anonpy.AnonPy.preview")
    def test_preview(self: Self, mock_preview: MagicMock) -> None:
        # Arrange
        args = {"resource": MockPixelDrain.id}
        self.anon.preview = mock_preview
        self.anon.preview.return_value = MockPixelDrain.get_preview_response(http_code=200)

        # Act
        preview = self.anon.preview(**args)

        # Assert
        self.anon.preview.assert_called_once_with(**args)
        self.assertTrue(preview.get("success", False))
        self.assertEqual(preview.get("downloads", -1), 1)
        self.assertEqual(len(preview.keys()), 24)

    @patch("anonpy.AnonPy.download")
    def test_download(self: Self, mock_download: MagicMock) -> None:
        # Arrange
        args = {"resource": MockPixelDrain.id, "path": Path.home()}
        self.anon.download = mock_download
        self.anon.download.return_value = MockPixelDrain.get_download_response(http_code=200)

        # Act
        download = self.anon.download(**args)

        # Assert
        self.anon.download.assert_called_once_with(**args)
        self.assertFalse(download.closed)
        self.assertGreater(len(download.getvalue()), 0)
