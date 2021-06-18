from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.catalog.db.base import Base


class ExtraTag(Base):

    __tablename__ = 'extra_tag'

    id_ = Column('id', Integer, primary_key=True)
    extra_tag = Column(Text, nullable=False, unique=True)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
