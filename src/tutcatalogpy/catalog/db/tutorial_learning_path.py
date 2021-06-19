from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from tutcatalogpy.catalog.db.base import Base


class TutorialLearningPath(Base):

    __tablename__ = 'tutorial_learning_path'

    tutorial_id = Column(Integer, ForeignKey('tutorial.id'), primary_key=True)
    learning_path_id = Column(Integer, ForeignKey('learning_path.id'), primary_key=True)
    index = Column(Integer)  # index in learning path

    tutorial = relationship('Tutorial', backref='learning_paths')
    learning_path = relationship('LearningPath', backref='tutorials')


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
