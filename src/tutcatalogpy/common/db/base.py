import enum
from typing import Final

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

FIELD_SEPARATOR: Final[str] = ','


class Search(int, enum.Enum):
    label: str

    def __new__(cls, value: int, label: str = '') -> 'Search':
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    EXCLUDE = (-1, '-')
    IGNORED = 0
    INCLUDE = (1, '+')
