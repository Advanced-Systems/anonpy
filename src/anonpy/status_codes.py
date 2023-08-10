#!/usr/bin/env python3

from enum import Enum, unique
from typing import Self

@unique
class StatusCode(Enum):
    # Note that the API documentation doesn't contain a definition for a successful
    # request. The ServerResponse dataclass that uses this enum in its status_code
    # property returns StatusCode.OK if its status property is true. The status
    # property only flips to false if an error occurred, in which event any other
    # status code may be returned.
    OK = 0
    ERROR_FILE_NOT_PROVIDED = 10
    ERROR_FILE_EMPTY = 11
    ERROR_FILE_INVALID = 12
    ERROR_USER_MAX_FILES_PER_HOUR_REACHED = 20
    ERROR_USER_MAX_FILES_PER_DAY_REACHED = 21
    ERROR_USER_MAX_BYTES_PER_HOUR_REACHED = 22
    ERROR_USER_MAX_BYTES_PER_DAY_REACHED = 23
    ERROR_FILE_DISALLOWED_TYPE = 30
    ERROR_FILE_SIZE_EXCEEDED = 31
    ERROR_FILE_BANNED = 32
    STATUS_ERROR_SYSTEM_FAILURE = 40
    # The documentation doesn't define this status code either, but as opposed
    # to StatusCode.OK, the server actually does return this error type if a file
    # doesn't exist (anymore)
    ERROR_FILE_NOT_FOUND = 404

    def __str__(self: Self) -> str:
        # The status_code property of the ServerResponse dataclass is capable
        # of setting the doc string in the event of a bad request at runtime
        return " ".join(
            filter(None, [
                str(self.value),
                self.name,
                self.__doc__
            ])
        )
