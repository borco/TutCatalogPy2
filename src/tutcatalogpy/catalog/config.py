import logging
from enum import Enum
from pathlib import Path
from typing import Optional, TextIO

import yaml
from PySide2.QtCore import QObject, Signal

from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Config(QObject):

    file_name: Optional[str] = None

    loaded = Signal()

    class CacheType(str, Enum):
        SQLITE = 'sqlite'

    def load(self, file_name: Optional[str] = None) -> None:
        log.info('Loading %s', file_name)
        self.file_name = file_name
        if file_name is not None:
            try:
                self.load_stream(file_name, open(file_name, encoding='utf-8', mode='r'))
            except Exception as e:
                log.warning('Could not load config %s: %s', file_name, str(e))
                self.clear()
        else:
            self.clear()
        self.loaded.emit()

    def load_stream(self, file_name: str, stream: TextIO) -> None:
        data = yaml.load(stream, Loader=yaml.CLoader) or {}
        self.__config_cache(file_name, data.get('cache', {}))
        self.__config_disks(data.get('disks', []))

    def clear(self):
        dal.disconnect()

    def __config_cache(self, file_name: str, data) -> None:
        cache_type = data.get('type')

        if cache_type is None:
            cache_type = Config.CacheType.SQLITE.value

        if cache_type == Config.CacheType.SQLITE.value:
            path = data.get('path')
            if path is not None and path != '':
                p = Path(path)
                if not p.is_absolute() and file_name is not None:
                    path = str(Path(file_name).expanduser().absolute().parent / path)
                path = '/' + path
            elif file_name != '':
                path = str(Path(file_name).expanduser().absolute().with_suffix('.db'))
                path = '/' + path
            else:
                raise RuntimeError('sqlite cache path not set')
            connection_string = f'sqlite://{path}'
        else:
            raise RuntimeError(f'cache not supported: {cache_type}')

        dal.connect(connection_string)

    def __config_disks(self, data) -> None:
        session = dal.session

        if len(data) == 0 or session is None:
            return

        (
            session
            .query(Disk)
            .update({Disk.status: Disk.Status.UNKNOWN})
        )

        for index, d in enumerate(data):
            path = d['path']
            if path == '' or path is None:
                raise ValueError("path can't be empty")

            path = Path(path).expanduser().absolute()
            pp = str(path.parent)
            pn = path.name

            disk = session.query(Disk).filter_by(disk_parent=pp, disk_name=pn).first()
            if disk is None:
                disk = Disk(disk_parent=pp, disk_name=pn)
                session.add(disk)

            disk.index_ = index + 1
            disk.location = Disk.Location(d.get('location', Disk.Location.REMOTE))
            disk.role = Disk.Role(d.get('role', Disk.Role.DEFAULT))
            disk.depth = int(d.get('depth', 1))
            disk.online = path.exists()
            disk.status = Disk.Status.OK

        # delete disks that still have their status set to UNKNOWN
        # we must use 'session.delete()' to make sqlachemy delete the associated folders
        for disk in session.query(Disk).filter(Disk.status == Disk.Status.UNKNOWN):
            session.delete(disk)

        session.commit()


config = Config()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
