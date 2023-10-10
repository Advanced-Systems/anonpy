#!/usr/bin/env python3

import json
from logging import Formatter, LogRecord
from typing import Dict, Optional, Self, override


class JsonFormatter(Formatter):
    def __init__(
            self: Self,
            fmt_dict: Optional[Dict]=None,
            time_format: str="%Y-%m-%dT%H:%M:%S",
            msec_format: str="%s.%03dZ"
        ) -> None:
        # The code for this class is based on an answer by Bogdan Mircea on Stack Overflow:
        # https://stackoverflow.com/a/70223539/10827244
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"timestamp": "asctime", "level": "levelname", "message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    @override
    def usesTime(self) -> bool:
        """
        Check if the format uses the creation time of the record.
        """
        return "asctime" in self.fmt_dict.values()

    @override
    def formatMessage(self: Self, record: LogRecord) -> Dict:
        """
        Return the specified record as JSON.
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    @override
    def format(self: Self, record: LogRecord) -> Dict:
        """
        Format the specified record as JSON.
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)

