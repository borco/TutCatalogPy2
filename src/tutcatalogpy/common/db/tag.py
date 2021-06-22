import enum

from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.common.db.base import Base, Search


class Tag(Base):

    class Source(enum.IntEnum):
        PUBLISHER = 0
        EXTRA = 1

    __tablename__ = 'tag'

    id_ = Column('id', Integer, primary_key=True)
    name = Column(Text, nullable=False)
    source = Column(Integer, default=Source.PUBLISHER)
    search = Column(Integer, default=Search.IGNORED)

    __table_args__ = (
        UniqueConstraint('name', 'source'),
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
