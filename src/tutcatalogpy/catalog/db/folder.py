from datetime import datetime
import enum

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
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
    disk_id = Column(Integer, ForeignKey('disk.id'), nullable=False)
    folder_parent = Column(Text, unique=False, nullable=True)
    folder_name = Column(Text, unique=False, nullable=True)
    system_id = Column(Text, default='', nullable=False)
    status = Column(Integer, default=Status.UNKNOWN, nullable=False)
    created = Column(DateTime, default=datetime.today(), nullable=False)
    modified = Column(DateTime, default=datetime.today(), nullable=False)
    size = Column(Integer, default=None, nullable=True)

    disk = relationship('Disk', back_populates='folders')

    __table_args__ = (
        UniqueConstraint('disk_id', 'folder_parent', 'folder_name'),
        UniqueConstraint('disk_id', 'system_id'),
    )
