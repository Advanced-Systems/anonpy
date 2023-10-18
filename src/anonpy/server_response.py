#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServerResponse:
    name: str
    folder: Path
    size: int
    resource: str
    url: str
