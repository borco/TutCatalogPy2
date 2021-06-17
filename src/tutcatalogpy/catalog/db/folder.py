import enum
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, Text

from tutcatalogpy.catalog.db.base import Base


class Folder(Base):

    class Status(enum.IntEnum):
        UNKNOWN = -1
        OK = 0
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
    status = Column(Integer, default=Status.OK, nullable=False)
    created = Column(DateTime, default=datetime.today(), nullable=False)
    modified = Column(DateTime, default=datetime.today(), nullable=False)
    size = Column(Integer, default=None, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)

    disk = relationship('Disk', back_populates='folders')
    cover = relationship('Cover', back_populates='folder', cascade='all, delete')

    __table_args__ = (
        UniqueConstraint('disk_id', 'folder_parent', 'folder_name'),
        UniqueConstraint('disk_id', 'system_id'),
    )

    def path(self) -> Path:
        return self.disk.path() / self.folder_parent / self.folder_name
