from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.catalog.db.base import Base


class LearningPath(Base):

    __tablename__ = 'learning_path'

    id_ = Column('id', Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    learning_path = Column(Text, nullable=False)

    publisher = relationship('Publisher', backref='learning_paths')

    __table_args__ = (
        UniqueConstraint('publisher_id', 'learning_path'),
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
