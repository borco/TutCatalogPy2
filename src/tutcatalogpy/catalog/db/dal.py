import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tutcatalogpy.catalog.db.base import Base

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DataAccessLayer:

    def __init__(self):
        self.__engine = None
        self.session = None

    def connect(self, connection: str):
        from tutcatalogpy.catalog.db.disk import Disk  # noqa: F401

        self.disconnect()

        log.info('Creating engine %s', connection)
        self.__engine = create_engine(connection)
        Base.metadata.create_all(self.__engine)

        self.Session = sessionmaker(bind=self.__engine)

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


dal = DataAccessLayer()
