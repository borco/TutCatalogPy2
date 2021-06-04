from enum import Enum


class TableColumnEnum(bytes, Enum):
    label: str
    column: str

    def __new__(cls, value: int, label: str, column: str):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.column = column
        return obj
