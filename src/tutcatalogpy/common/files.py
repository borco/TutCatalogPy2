"""Various utility functions."""

import logging
import os
import platform
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def relative_path(reference: str, name: str) -> str:
    """Return a file located in the same dir with reference.

    :param reference: usually __file__
    :param name: the name of the file you actually want
    :return: name appended to the reference's parent folder
    """
    return str(Path(reference).parent / name)


def get_creation_datetime(stat: os.stat_result) -> datetime:
    # reference: https://www.codegrepper.com/code-examples/python/python+get+file+date+creation
    try:
        return datetime.fromtimestamp(stat.st_birthtime)
    except AttributeError:
        if platform.system() == 'Windows':
            return datetime.fromtimestamp(stat.st_ctime)
        else:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.fromtimestamp(stat.st_mtime)


def get_modification_datetime(stat: os.stat_result) -> datetime:
    return datetime.fromtimestamp(stat.st_mtime)


def get_folder_size(path: Path) -> int:
    """Compute the size of a folder and its subfolders."""
    size: int = 0
    count: int = 0

    for root, _, files in os.walk(path):
        p = Path(root)
        for name in files:
            size += (p / name).stat().st_size
            count += 1

    log.debug('Folder size: %s: %d (%d files)', path, size, count)
    return size
