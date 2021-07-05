from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.common.db.base import Base
from tutcatalogpy.common.db.search_flag import Search


class Author(Base):

    __tablename__ = 'author'

    id_ = Column('id', Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    search = Column(Integer, default=Search.IGNORED)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
