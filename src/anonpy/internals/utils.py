#!/usr/bin/env python3

from typing import Any, List, Dict, Iterable
from tqdm import tqdm
from requests_toolbelt import MultipartEncoderMonitor

def unique(list_: List[Any]) -> List[Any]:
    """
    Remove all duplicated entries from a list.
    """
    return list(dict.fromkeys(list_))

def _progressbar_options(
            iterable: Iterable,
            desc: str,
            unit: str,
            color: str="\033[32m",
            char: str='\u25CB',
            total: int=None,
            disable: bool=False
        ) -> Dict:
        """
        Return custom optional arguments for `tqdm` progressbars.
        """
        return {
            'iterable': iterable,
            'bar_format': "{l_bar}%s{bar}%s{r_bar}" % (color, "\033[0m"),
            'ascii': char.rjust(9, ' '),
            'desc': desc,
            'unit': unit.rjust(1, ' '),
            'unit_scale': True,
            'unit_divisor': 1024,
            'total': len(iterable) if total is None else total,
            'disable': not disable
        }

def _callback(monitor: MultipartEncoderMonitor, tqdm_handler: tqdm) -> None:
    """
    Defines a multi-part encoder monitor callback function for progress feedback.
    """
    tqdm_handler.total = monitor.len
    tqdm_handler.update(monitor.bytes_read - tqdm_handler.n)
