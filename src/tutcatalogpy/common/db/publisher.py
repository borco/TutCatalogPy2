from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.common.db.base import Base


class Publisher(Base):

    __tablename__ = 'publisher'

    id_ = Column('id', Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
