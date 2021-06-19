import logging
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer

from tutcatalogpy.catalog.db.base import Base

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


tutorial_author_table = Table(
    'tutorial_author',
    Base.metadata,
    Column('tutorial_id', Integer, ForeignKey('tutorial.id')),
    Column('author_id', Integer, ForeignKey('author.id')),
)

tutorial_extra_tag_table = Table(
    'tutorial_extra_tag',
    Base.metadata,
    Column('tutorial_id', Integer, ForeignKey('tutorial.id')),
    Column('extra_tag_id', Integer, ForeignKey('extra_tag.id')),
)

tutorial_tag_table = Table(
    'tutorial_tag',
    Base.metadata,
    Column('tutorial_id', Integer, ForeignKey('tutorial.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
)


class DataAccessLayer:

    def __init__(self):
        self.__engine: Optional[Engine] = None
        self.session: Optional[Session] = None

    def connect(self, connection: str):
        from tutcatalogpy.catalog.db.author import Author  # noqa: F401
        from tutcatalogpy.catalog.db.cover import Cover  # noqa: F401
        from tutcatalogpy.catalog.db.disk import Disk  # noqa: F401
        from tutcatalogpy.catalog.db.extra_tag import ExtraTag  # noqa: F401
        from tutcatalogpy.catalog.db.folder import Folder  # noqa: F401
        from tutcatalogpy.catalog.db.learning_path import LearningPath  # noqa: F401
        from tutcatalogpy.catalog.db.publisher import Publisher  # noqa: F401
        from tutcatalogpy.catalog.db.tag import Tag  # noqa: F401
        from tutcatalogpy.catalog.db.tutorial import Tutorial  # noqa: F401
        from tutcatalogpy.catalog.db.tutorial_learning_path import TutorialLearningPath  # noqa: F401

        self.disconnect()

        log.info('Creating engine %s', connection)
        self.__engine = create_engine(connection)
        Base.metadata.create_all(self.__engine)

        self.Session = sessionmaker(bind=self.__engine)

        self.session = self.Session()

    def renew_session(self) -> None:
        if self.session is not None:
            self.session.close()
        self.session = self.Session()

    def disconnect(self) -> None:
        if self.session is not None:
            log.debug('Closing GUI session.')
            self.session.close()
            self.session = None
        if self.__engine is not None:
            log.debug('Disposing the old engine.')
            self.__engine.dispose()
            self.__engine = None

    @property
    def connected(self) -> bool:
        return self.__engine is not None and self.session is not None

    @property
    def url(self) -> str:
        return str(self.__engine.url) if self.__engine is not None else ''


dal = DataAccessLayer()
