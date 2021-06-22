from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, Text

from tutcatalogpy.common.db.base import Base, Search


class LearningPath(Base):

    __tablename__ = 'learning_path'

    id_ = Column('id', Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    title = Column(Text, nullable=False)
    search = Column(Integer, default=Search.IGNORED)

    publisher = relationship('Publisher', backref='learning_paths')

    __table_args__ = (
        UniqueConstraint('publisher_id', 'title'),
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
