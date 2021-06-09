import enum
from pathlib import Path

from sqlalchemy import Boolean, Column, Enum, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

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
        UNKNOWN = -1
        OK = 0

    __tablename__ = 'disk'
    id_ = Column('id', Integer, primary_key=True)
    index_ = Column('index', Integer, nullable=False)
    disk_parent = Column(Text, nullable=False)
    disk_name = Column(Text, nullable=False)
    location = Column(Enum(Location), default=Location.LOCAL, nullable=False)
    role = Column(Enum(Role), default=Role.DEFAULT, nullable=False)
    depth = Column(Integer, default=0, nullable=False)
    checked = Column(Boolean, default=True, nullable=False)
    online = Column(Boolean, default=False, nullable=False)
    status = Column(Integer, default=Status.OK, nullable=False)

    # https://esmithy.net/2020/06/20/sqlalchemy-cascade-delete/
    folders = relationship('Folder', back_populates='disk', cascade='all, delete')

    __table_args__ = (
        UniqueConstraint('disk_parent', 'disk_name'),
    )

    def path(self) -> Path:
        return Path(self.disk_parent) / self.disk_name
