
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.catalog.db.base import Base


class Tutorial(Base):

    __tablename__ = 'tutorial'

    id_ = Column('id', Integer, primary_key=True)
    title = Column(Text, nullable=False)

    authors = relationship(
        'Author',
        secondary='tutorial_author',
        backref='tutorials'
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
