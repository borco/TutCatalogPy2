import shutil
from pathlib import Path
from typing import Final

from pytest import fixture

from tutcatalogpy.catalog.scan_worker import ScanWorker
from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
import tutcatalogpy.common.logging_config  # noqa: F401


@fixture
def session():
    dal.connect('sqlite:///:memory:')
    yield dal.Session()
    dal.disconnect()


def test_scan_disks_for_offline_disks(tmp_path, session):
    PATH_PARENT: Final[str] = str(tmp_path)
    PATH_NAME: Final[str] = 'foo'
    disk_path: Path = tmp_path / PATH_NAME

    session.add(Disk(path_parent=PATH_PARENT, path_name=PATH_NAME, index_=0))
    session.commit()

    worker = ScanWorker()

    shutil.rmtree(disk_path, ignore_errors=True)
    worker._ScanWorker__scan_disks(session)
    assert session.query(Disk).one().online is False


def test_scan_disks_for_online_disks(tmp_path, session):
    PATH_PARENT: Final[str] = str(tmp_path)
    PATH_NAME: Final[str] = 'foo'
    disk_path: Path = tmp_path / PATH_NAME

    session.add(Disk(path_parent=PATH_PARENT, path_name=PATH_NAME, index_=0))
    session.commit()

    worker = ScanWorker()

    disk_path.mkdir()
    worker._ScanWorker__scan_disks(session)
    assert session.query(Disk).one().online is True


def test_scan_disks_updates_online(tmp_path, session):
    PATH_PARENT: Final[str] = str(tmp_path)
    PATH_NAME: Final[str] = 'foo'
    disk_path: Path = tmp_path / PATH_NAME

    session.add(Disk(path_parent=PATH_PARENT, path_name=PATH_NAME, index_=0))
    session.commit()

    worker = ScanWorker()

    disk_path.mkdir()
    worker._ScanWorker__scan_disks(session)
    assert session.query(Disk).one().online is True

    shutil.rmtree(disk_path, ignore_errors=True)
    worker._ScanWorker__scan_disks(session)
    assert session.query(Disk).one().online is False

    disk_path.mkdir(mode=0o777)
    worker._ScanWorker__scan_disks(session)
    assert session.query(Disk).one().online is True
