#!/usr/bin/env python3

from io import BytesIO
from typing import Dict, Self, Type

class MockPixelDrain:
    id = "1tdWj9g2"

    @classmethod
    def get_upload_response(cls: Type[Self], http_code: int) -> Dict:
        match http_code:
            case 200: # OK
                return {
                    "success": True,
                    "id": cls.id
                }
            case 413: # Payload Too Large
                return {
                    "success": False,
                    "value": "file_too_large",
                    "message": "The file you tried to upload is too large"
                }
            case 422: # Unprocessable Entity
                return {
                    "success": False,
                    "value": "no_file",
                    "message": "The file does not exist or is empty."
                }
            case 500: # Internal Server Error
                return {
                    "success": False,
                    "value": "internal",
                    "message": "An internal server error occurred."
                }
            case _:
                raise NotImplementedError()

    @classmethod
    def get_preview_response(cls: Type[Self], http_code: int) -> Dict:
        match http_code:
            case 200: # OK
                return {
                    "success": True,
                    "id": cls.id,
                    "name": "inkscape.exe",
                    "size": 453281,
                    "views": 2,
                    "bandwidth_used": 453281,
                    "bandwidth_used_paid": 0,
                    "downloads": 1,
                    "date_upload": "2023-08-30T16:08:27.647Z",
                    "date_last_view": "2023-09-06T19:21:12.431Z",
                    "mime_type": "application/vnd.microsoft.portable-executable",
                    "thumbnail_href": "/file/1tdWj9g2/thumbnail",
                    "hash_sha256": "f11f45487f5e04f161de1691e8b3baa718bc99b210c70735503a4a43eb26cba0",
                    "delete_after_date": "0001-01-01T00:00:00Z",
                    "delete_after_downloads": 0,
                    "availability": "",
                    "availability_message": "",
                    "abuse_type": "",
                    "abuse_reporter_name": "",
                    "can_edit": False,
                    "can_download": True,
                    "show_ads": True,
                    "allow_video_player": False,
                    "download_speed_limit": 0
                }
            case 404: # Not Found
                return {
                    "success": False,
                    "value": "file_not_found"
                }
            case _:
                raise NotImplementedError()

    @staticmethod
    def get_download_response(http_code: int) -> Dict:
        match http_code:
            case 200: # OK
                return BytesIO("Dummy binary data: \x00\x01".encode("utf-8"))
            case 403: # Forbidden
                return {
                    "success": False,
                    "value": "file_rate_limited_captcha_required",
                    "message": "This file is using too much bandwidth. For anonymous downloads a captcha is required now. The captcha entry is available on the download page"
                }
            case 404: # Not Found
                return {
                    "success": False,
                    "value": "not_found",
                    "message": "The entity you requested could not be found"
                }
            case _:
                raise NotImplementedError()
