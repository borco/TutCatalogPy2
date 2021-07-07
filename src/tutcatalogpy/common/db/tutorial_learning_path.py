from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean, Integer

from tutcatalogpy.common.db.base import Base


class TutorialLearningPath(Base):

    __tablename__ = 'tutorial_learning_path'

    id_ = Column('id', Integer, primary_key=True)
    tutorial_id = Column(Integer, ForeignKey('tutorial.id'))
    learning_path_id = Column(Integer, ForeignKey('learning_path.id'))
    index = Column(Integer)  # index in learning path
    show_in_title = Column(Boolean)

    tutorial = relationship('Tutorial', backref='learning_paths')
    learning_path = relationship('LearningPath', backref='tutorials')

    __table_args__ = (
        UniqueConstraint('tutorial_id', 'learning_path_id'),
    )


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
