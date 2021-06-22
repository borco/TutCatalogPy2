from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.common.db.base import Base


class Tutorial(Base):

    __tablename__ = 'tutorial'

    id_ = Column('id', Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    title = Column(Text, nullable=False)

    authors = relationship('Author', secondary='tutorial_author', backref='tutorials')
    tags = relationship('Tag', secondary='tutorial_tag', backref='tutorials')

    publisher = relationship('Publisher', backref=backref('tutorials'))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
