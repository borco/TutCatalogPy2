import enum
from typing import Optional

from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, Text

from tutcatalogpy.common.db.base import Base


class Tutorial(Base):

    class Status(enum.IntEnum):
        UNKNOWN = -1
        OK = 0
        CHANGED = enum.auto()
        RENAMED = enum.auto()
        NEW = enum.auto()
        DELETED = enum.auto()

    class Progress(bytes, enum.Enum):
        label: str

        def __new__(cls, value: int, label: str):
            obj = bytes.__new__(cls, [value])
            obj._value_ = value
            obj.label = label
            return obj

        @classmethod
        def value_for(cls, label: str) -> Optional['Progress']:
            for item in list(cls):
                if item.label == label:
                    return item.value

        NOT_STARTED = (0, 'not started')
        STARTED = (1, 'started')
        FINISHED = (2, 'finished')

    __tablename__ = 'tutorial'

    id_ = Column('id', Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    title = Column(Text, default='', nullable=False)
    released = Column(Text, default='', nullable=False)
    duration = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    url = Column(Text, default='', nullable=False)
    description = Column(Text, default='', nullable=False)

    is_complete = Column(Boolean, default=True, nullable=False)
    is_online = Column(Boolean, default=False, nullable=False)
    todo = Column(Boolean, default=False, nullable=False)
    progress = Column(Integer, default=Progress.NOT_STARTED.value, nullable=False)
    rating = Column(Integer, default=0, nullable=False)

    # aggregate fields used by models to search and filter and by view to display
    # separator: base.FIELD_SEPARATOR
    # example: ',A Field,Another Field,One More Field,'
    all_authors = Column(Text, default='', nullable=False)
    all_tags = Column(Text, default='', nullable=False)
    all_learning_paths = Column(Text, default='', nullable=False)

    status = Column(Integer, default=Status.OK, nullable=False)

    system_id = Column(Text)
    created = Column(DateTime)
    modified = Column(DateTime)
    size = Column(Integer)

    authors = relationship('Author', secondary='tutorial_author', backref='tutorials')
    tags = relationship('Tag', secondary='tutorial_tag', backref='tutorials')
    publisher = relationship('Publisher', backref=backref('tutorials'))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
