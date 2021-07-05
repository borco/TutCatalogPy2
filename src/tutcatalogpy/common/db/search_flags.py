import enum

from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer

from tutcatalogpy.common.db.base import Base


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


class SearchFlags(Base):
    class Type(enum.IntEnum):
        IS_COMPLETE = 0
        IS_ONLINE = enum.auto()

    __tablename__ = 'search_flags'

    id_ = Column('id', Integer, primary_key=True)
    value = Column(Integer, nullable=False, unique=True)
    search = Column(Integer, default=Search.IGNORED)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
