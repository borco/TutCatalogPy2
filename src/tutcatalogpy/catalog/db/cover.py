from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, LargeBinary, Text

from tutcatalogpy.catalog.db.base import Base


class Cover(Base):

    __tablename__ = 'cover'

    id_ = Column('id', Integer, primary_key=True)
    folder_id = Column(Integer, ForeignKey('folder.id'), nullable=False, unique=True)
    system_id = Column(Text, default=None, nullable=True)
    created = Column(DateTime, default=None, nullable=True)
    modified = Column(DateTime, default=None, nullable=True)
    size = Column(Integer, default=None, nullable=True)
    data = Column(LargeBinary, default=None, nullable=True)

    folder = relationship('Folder', back_populates='cover')
