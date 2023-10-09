#!/usr/bin/env python3

from logging import Formatter, LogRecord
from typing import Dict, Optional, Self, override


class CsvFormatter(Formatter):
    def __init__(
            self: Self,
            sep: str=",",
            fmt_dict: Optional[Dict]=None,
            time_format: str="%Y-%m-%dT%H:%M:%S",
            msec_format: str="%s.%03dZ"
        ) -> None:
        self.sep = sep
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"timestamp": "asctime", "level": "levelname", "message": "message"}
        self.header = list(self.fmt_dict.keys())
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
    def formatMessage(self, record: LogRecord) -> str:
        """
        Return the specified record as CSV.
        """
        return self.sep.join([
            # Enclose message in double-quotes in case it contains the sep character
            "\"%s\"" % record.__dict__[fmt_val]
            if fmt_key == "message"
            else str(record.__dict__[fmt_val])
            for fmt_key, fmt_val in self.fmt_dict.items()
        ])

    @override
    def format(self: Self, record: LogRecord) -> str:
        """
        Format the specified record as CSV.
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        # The code below is largely borrowed from the parent's class method
        message = self.formatMessage(record)

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if message[-1:] != "\n":
                message = "%s\n" % message
            message = "%s%s" % (message, record.exc_text)

        if record.stack_info:
            if message[-1:] != "\n":
                message = "%s\n" % message
            message = "%s%s" % (message, self.formatStack(record.stack_info))

        return message
