import enum

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from tutcatalogpy.catalog.db.base import Base


class Folder(Base):

    class Status(enum.IntEnum):
        UNKNOWN = 0
        UNCHANGED = enum.auto()
        CHANGED = enum.auto()
        RENAMED = enum.auto()
        NEW = enum.auto()
        DELETED = enum.auto()

    __tablename__ = 'folder'

    id_ = Column('id', Integer, primary_key=True)
    disk_id = Column(Integer, ForeignKey('disk.id'))
    tutorial_path = Column(Text, unique=False, nullable=True)
    tutorial_name = Column(Text, unique=False, nullable=True)
    system_id = Column(Text, unique=True)
    status = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)
    size = Column(Integer, default=None, nullable=True)
