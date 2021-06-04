from enum import Enum


class LabeledEnum(bytes, Enum):
    label: str

    def __new__(cls, value: int, label: str):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        return obj
