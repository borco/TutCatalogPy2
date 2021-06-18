from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer

from tutcatalogpy.catalog.db.base import Base


class TutorialLearningPath(Base):

    __tablename__ = 'tutorial_learning_path'

    tutorial_id = Column(Integer, ForeignKey('tutorial.id'))
    learning_path_id = Column(Integer, ForeignKey('learning_path.id'))

    index = Column(Integer)  # index in learning path

    tutorial = relationship('Tutorial', backref='learning_paths')
    learning_path = relationship('LearningPath', backref='tutorials')

    __table_args__ = (
        PrimaryKeyConstraint('tutorial_id', 'learning_path_id'),
        UniqueConstraint('learning_path_id', 'index'),
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
