from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, LargeBinary, Text

from tutcatalogpy.common.db.base import Base


class Image(Base):

    __tablename__ = 'image'

    id_ = Column('id', Integer, primary_key=True)
    folder_id = Column(Integer, ForeignKey('folder.id'))
    name = Column(Text, nullable=False)
    system_id = Column(Text, nullable=False)
    created = Column(DateTime, nullable=True)
    modified = Column(DateTime, nullable=True)
    size = Column(Integer, nullable=True)
    data = Column(LargeBinary, nullable=True)

    folder = relationship('Folder', backref=backref('images'))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
