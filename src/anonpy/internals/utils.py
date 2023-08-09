#!/usr/bin/env python3

from typing import Any, List

def unique(list_: List[Any]) -> List[Any]:
    """
    Remove all duplicated entries in a list.
    """
    return list(dict.fromkeys(list_))
