from enum import Enum

from sqlalchemy.sql.schema import Column


class DbTableColumnEnum(bytes, Enum):
    label: str  # column label displayed in the table view
    attr: str  # query attribute name
    column: Column  # ORM column

    def __new__(cls, value: int, label: str, attr: str, column: Column):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.attr = attr
        obj.column = column
        return obj
