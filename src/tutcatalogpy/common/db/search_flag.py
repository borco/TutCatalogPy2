import enum
from sqlalchemy.orm.session import Session

from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer

from tutcatalogpy.common.db.base import Base


class LabeledIntEnum(int, enum.Enum):
    label: str

    def __new__(cls, value: int, label: str = '') -> 'LabeledIntEnum':
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj


class Search(LabeledIntEnum):
    EXCLUDE = (-1, '-')
    IGNORED = 0
    INCLUDE = (1, '+')


class SearchValue(LabeledIntEnum):
    IS_COMPLETE = (0, 'complete')
    HAS_ERROR = (1, 'errors')


class SearchFlag(Base):

    __tablename__ = 'search_flag'

    id_ = Column('id', Integer, primary_key=True)
    value = Column(Integer, nullable=False, unique=True)
    search = Column(Integer, default=Search.IGNORED)

    @staticmethod
    def init_with_default_values(session: Session) -> None:
        dirty: bool = False
        for value in SearchValue:
            flag = session.query(SearchFlag).filter_by(value=value).first()
            if flag is None:
                session.add(SearchFlag(value=value))
                dirty = True
        if dirty:
            session.commit()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
