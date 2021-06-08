import enum
from pathlib import Path

from sqlalchemy import Boolean, Column, Enum, Integer, Text, UniqueConstraint

from tutcatalogpy.catalog.db.base import Base


class Disk(Base):
    class Location(str, enum.Enum):
        LOCAL = 'local'
        REMOTE = 'remote'

    class Role(str, enum.Enum):
        DEFAULT = ''
        BACKUP = 'backup'
        UPLOADS = 'uploads'
        SCHEDULED = 'scheduled'

    class Status(enum.IntEnum):
        OK = 0
        UNKNOWN = enum.auto()

    __tablename__ = 'disk'
    id_ = Column('id', Integer, primary_key=True)
    index_ = Column('index', Integer, nullable=False)
    path_parent = Column(Text, nullable=False)
    path_name = Column(Text, nullable=False)
    location = Column(Enum(Location), default=Location.LOCAL, nullable=False)
    role = Column(Enum(Role), default=Role.DEFAULT, nullable=False)
    depth = Column(Integer, default=0, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    online = Column(Boolean, default=False, nullable=False)
    status = Column(Integer, default=Status.OK, nullable=False)

    __table_args__ = (
        UniqueConstraint('path_parent', 'path_name'),
    )

    def path(self) -> Path:
        return Path(self.path_parent) / self.path_name
