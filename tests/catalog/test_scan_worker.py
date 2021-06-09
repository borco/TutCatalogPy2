import shutil
from pathlib import Path
from typing import Final, List

from pytest import fixture, mark
from sqlalchemy.orm.session import Session

from tutcatalogpy.catalog.scan_config import ScanConfig
from tutcatalogpy.catalog.scan_worker import ScanWorker
from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
from tutcatalogpy.catalog.db.folder import Folder
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


@mark.parametrize(
    'folder_names',
    [
        (),
        ('folder1',),
        ('folder1', 'folder2'),
    ]
)
def test_scan_folders_for_new_db(tmp_path: Path, session: Session, folder_names: List[str]):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'disk1'
    disk_path: Path = tmp_path / DISK_NAME

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0, online=True))
    session.commit()

    disk_path.mkdir()
    for name in folder_names:
        (disk_path / name).mkdir(parents=True)

    mode = ScanConfig.Mode.EXTENDED
    worker = ScanWorker()
    worker.scan(mode)

    assert {x for x, in session.query(Folder.folder_name).all()} == set(folder_names)


@mark.parametrize(
    'folder_names, deleted_names, remaining_names',
    [
        (['folder1'], [], ['folder1']),
        (['folder1'], ['folder1'], []),
        (['folder1', 'folder2'], ['folder2'], ['folder1']),
        (['folder1', 'folder2'], ['folder1'], ['folder2']),
        (['folder1', 'folder2'], ['folder1', 'folder2'], []),
    ]
)
def test_scan_folders_removes_deleted_folders(tmp_path: Path, session: Session, folder_names: List[str], deleted_names: List[str], remaining_names: List[str]):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'disk1'
    disk_path: Path = tmp_path / DISK_NAME

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0, online=True))
    session.commit()

    disk_path.mkdir()
    for name in folder_names:
        (disk_path / name).mkdir(parents=True)

    mode = ScanConfig.Mode.EXTENDED
    worker = ScanWorker()
    worker.scan(mode)

    for name in deleted_names:
        shutil.rmtree(disk_path / name, ignore_errors=True)

    worker.scan(mode)

    assert {x for x, in session.query(Folder.folder_name).all()} == set(remaining_names)


def test_scan_folders_recognizes_moved_folders(tmp_path: Path, session: Session):
    DISK_PARENT: Final[str] = str(tmp_path)
    DISK_NAME: Final[str] = 'disk1'
    FOLDER_NAME1: Final[str] = 'folder1'
    FOLDER_NAME2: Final[str] = 'folder2'
    FOLDER_NAME3: Final[str] = 'folder3'

    disk_path: Path = tmp_path / DISK_NAME

    session.add(Disk(disk_parent=DISK_PARENT, disk_name=DISK_NAME, index_=0, online=True))
    session.commit()

    disk_path.mkdir()
    (disk_path / FOLDER_NAME1).mkdir(parents=True)
    (disk_path / FOLDER_NAME2).mkdir(parents=True)

    mode = ScanConfig.Mode.EXTENDED
    worker = ScanWorker()
    worker.scan(mode)

    folder1_id = session.query(Folder).filter(Folder.folder_name == FOLDER_NAME1).one().id_

    (disk_path / FOLDER_NAME1).rename(disk_path / FOLDER_NAME3)

    worker.scan(mode)

    folder3_id = session.query(Folder).filter(Folder.folder_name == FOLDER_NAME3).one().id_

    assert folder1_id == folder3_id
