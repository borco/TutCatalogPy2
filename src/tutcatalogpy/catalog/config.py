import logging
from enum import Enum
from typing import Optional

from PySide2.QtCore import QObject, Signal
from ruamel.yaml import YAML

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Config(QObject):

    loaded = Signal()

    class CacheType(str, Enum):
        SQLITE = 'sqlite'
        MYSQL = 'mysql'

    def __init__(self) -> None:
        super().__init__()
        self.file_name: Optional[str] = None

    def load(self, file_name: Optional[str] = None) -> None:
        log.info('Loading %s', file_name)
        self.file_name = file_name
        if self.file_name is not None:
            with open(self.file_name, encoding='utf-8', mode='r') as f:
                yaml = YAML()
                data = yaml.load(f)
                self.config_cache(data.get('cache', {}), self.file_name)
                self.config_disks(data.get('disks', []))
        self.loaded.emit()

    def clear(self):
        pass

    def config_cache(self, data, file_name: str) -> None:
        log.info('data: %s', str(data))
        log.info('file name: %s', file_name)

    def config_disks(self, data) -> None:
        log.info('config disks: %s', str(data))


config = Config()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
