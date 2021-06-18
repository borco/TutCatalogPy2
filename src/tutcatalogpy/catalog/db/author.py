from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.catalog.db.base import Base


class Author(Base):

    __tablename__ = 'author'

    id_ = Column('id', Integer, primary_key=True)
    author = Column(Text, nullable=False)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
