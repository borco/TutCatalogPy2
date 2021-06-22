import enum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Search(enum.IntEnum):
    WITHOUT = -1
    IGNORED = 0
    WITH = 1
