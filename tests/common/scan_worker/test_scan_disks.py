import shutil
from pathlib import Path
from typing import Final

from pytest import fixture
from sqlalchemy.orm.session import Session

from tutcatalogpy.common.scan_config import ScanConfig
from tutcatalogpy.common.scan_worker import ScanWorker
from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk
import tutcatalogpy.common.logging_config  # noqa: F401


@fixture
# def session(tmp_path):
#     dal.connect(f'sqlite:///{tmp_path}/test.db')
def session() -> Session:
    dal.connect('sqlite:///:memory:')
    yield dal.Session()
    dal.disconnect()


def test_scan_disks_for_offline_disks(tmp_path: Path, session: Session):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'foo'

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0))
    session.commit()

    mode = ScanConfig.Mode.STARTUP
    worker = ScanWorker()
    worker.scan(mode)
    assert session.query(Disk).one().online is False


def test_scan_disks_for_online_disks(tmp_path: Path, session: Session):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'foo'
    disk_path: Path = tmp_path / DISK_NAME

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0))
    session.commit()

    disk_path.mkdir()

    mode = ScanConfig.Mode.STARTUP
    worker = ScanWorker()
    worker.scan(mode)
    assert session.query(Disk).one().online is True


def test_scan_disks_updates_online(tmp_path: Path, session: Session):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'foo'
    disk_path: Path = tmp_path / DISK_NAME

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0))
    session.commit()

    mode = ScanConfig.Mode.STARTUP
    worker = ScanWorker()

    disk_path.mkdir()
    worker.scan(mode)
    assert session.query(Disk).one().online is True

    shutil.rmtree(disk_path, ignore_errors=True)
    worker.scan(mode)
    assert session.query(Disk).one().online is False

    disk_path.mkdir()
    worker.scan(mode)
    assert session.query(Disk).one().online is True
