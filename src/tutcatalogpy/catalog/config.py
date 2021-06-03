import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from PySide2.QtCore import QObject, Signal
from ruamel.yaml import YAML

from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Config(QObject):

    file_name: Optional[str] = None

    loaded = Signal()

    class CacheType(str, Enum):
        SQLITE = 'sqlite'
        MYSQL = 'mysql'

    def load(self, file_name: Optional[str] = None) -> None:
        log.info('Loading %s', file_name)
        self.file_name = file_name
        if self.file_name is not None:
            try:
                with open(self.file_name, encoding='utf-8', mode='r') as f:
                    yaml = YAML()
                    data = yaml.load(f)
                    self.__config_cache(data.get('cache', {}), self.file_name)
                    self.__config_disks(data.get('disks', []))
            except Exception as e:
                log.warn('Could not load config %s: %s', file_name, str(e))
                self.clear()
        else:
            self.clear()
        self.loaded.emit()

    def clear(self):
        dal.disconnect()

    def __config_cache(self, data, file_name: str) -> None:
        cache_type = data.get('type')

        if cache_type is None:
            dal.connect('sqlite:///:memory:')
        elif cache_type == Config.CacheType.SQLITE.value:
            path = data.get('path')
            if path is not None and path != '':
                p = Path(path)
                if not p.is_absolute() and file_name is not None:
                    path = str(Path(file_name).absolute().parent / path)
                path = '/' + path
            else:
                raise RuntimeError('cache path not set')
            connection_string = f'sqlite://{path}'
            dal.connect(connection_string)
        else:
            raise RuntimeError(f'cache not supported: {cache_type}')

        dal.session = dal.Session()

    def __config_disks(self, data) -> None:
        if len(data) == 0:
            return

        session = dal.session

        for index, d in enumerate(data):
            path = d['path']
            if path == '' or path is None:
                raise ValueError("path can't be empty")

            path = Path(path).expanduser().absolute()
            pp = str(path.parent)
            pn = path.name

            disk = session.query(Disk).filter_by(path_parent=pp, path_name=pn).first()
            if disk is None:
                disk = Disk(path_parent=pp, path_name=pn)
                session.add(disk)

            disk.index_ = index
            disk.location = Disk.Location(d.get('location', Disk.Location.REMOTE))
            disk.role = Disk.Role(d.get('role', Disk.Role.DEFAULT))
            disk.depth = int(d.get('depth', 1))
            disk.monitored = d.get('monitored', False)
            disk.online = path.exists()

        session.commit()


config = Config()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
