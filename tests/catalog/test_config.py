from io import StringIO
from pathlib import Path
from typing import Final

import pytest

from tutcatalogpy.catalog.config import config
from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.db.folder import Folder


def test_empty_config_raises():
    with pytest.raises(RuntimeError) as excinfo:
        config.load_stream('', StringIO(''))
    assert str(excinfo.value) == 'sqlite cache path not set'


def test_sqlite_cache_inferred_from_config_file_name(tmp_path):
    config.load_stream(tmp_path / 'foo.yml', StringIO(''))
    assert dal.url == f'sqlite:///{tmp_path}/foo.db'


def test_sqlite_cache_with_explicit_path(tmp_path):
    config.load_stream('', StringIO(f"""
        cache:
            path: {tmp_path}/bar.db
    """))
    assert dal.url == f'sqlite:///{tmp_path}/bar.db'


def test_sqlite_cache_explicit_path_overrides_implicit_path(tmp_path):
    config.load_stream(tmp_path / 'foo.yml', StringIO(f"""
        cache:
            path: {tmp_path}/bar.db
    """))
    assert dal.url == f'sqlite:///{tmp_path}/bar.db'


def test_sqlite_cache_with_explicit_path_with_empty_file_name(tmp_path):
    config.load_stream('', StringIO(f"""
        cache:
            path: {tmp_path}/bar.db
    """))
    assert dal.url == f'sqlite:///{tmp_path}/bar.db'


def test_unknown_cache_type_raises():
    with pytest.raises(RuntimeError) as excinfo:
        config.load_stream('', StringIO("""
            cache:
                type: foo
        """))
    assert str(excinfo.value) == 'cache not supported: foo'


def test_load_config_with_one_disk(tmp_path):
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: downloads
                depth: 2
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG))

    disks = dal.session.query(Disk)

    assert disks.count() == 1

    disk = disks.one()

    assert disk.disk_parent == str(Path('~/Downloads/').expanduser().absolute())
    assert disk.disk_name == 'foo'
    assert disk.role == Disk.Role.DOWNLOADS
    assert disk.depth == 2
    assert disk.location == Disk.Location.LOCAL
    assert disk.id_ == 1
    assert disk.index_ == 1


def test_load_config_with_many_disk(tmp_path):
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG))

    disks = dal.session.query(Disk)

    assert disks.count() == 2

    disk = disks.offset(1).one()

    assert disk.disk_parent == str(Path('~/Downloads/').expanduser().absolute())
    assert disk.disk_name == 'bar'
    assert disk.role == Disk.Role.DEFAULT
    assert disk.depth == 2
    assert disk.location == Disk.Location.REMOTE
    assert disk.id_ == 2
    assert disk.index_ == 2


def test_reload_same_config_with_many_disk(tmp_path):
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
            -
                path: ~/Downloads/bar/
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG))
    config.load_stream(config_file, StringIO(CONFIG))

    disks = dal.session.query(Disk).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.disk_name == 'foo'
    assert disk.id_ == 1
    assert disk.index_ == 1

    disk = disks[1]

    assert disk.disk_name == 'bar'
    assert disk.id_ == 2
    assert disk.index_ == 2


def test_reload_config_with_many_disk_updates_disk_index(tmp_path):
    CONFIG1: Final[str] = """
        cache:
            type: sqlite
        disks:
            -
                path: ~/Downloads/foo/
            -
                path: ~/Downloads/bar/
    """

    CONFIG2: Final[str] = """
        cache:
            type: sqlite
        disks:
            -
                path: ~/Downloads/bar/
            -
                path: ~/Downloads/foo/
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG1))
    config.load_stream(config_file, StringIO(CONFIG2))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.disk_name == 'bar'
    assert disk.index_ == 1
    assert disk.id_ == 2

    disk = disks[1]

    assert disk.disk_name == 'foo'
    assert disk.index_ == 2
    assert disk.id_ == 1


def test_disks_removed_from_cache_when_removed_from_config(tmp_path):
    CONFIG1: Final[str] = """
        cache:
            type: sqlite

        disks:
            -
                path: ~/Downloads/foo/
            -
                path: ~/Downloads/bar/
    """

    CONFIG2: Final[str] = """
        cache:
            type: sqlite

        disks:
            -
                path: ~/Downloads/bar/
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG1))
    config.load_stream(config_file, StringIO(CONFIG2))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 1

    disk = disks[0]

    assert disk.disk_name == 'bar'
    assert disk.index_ == 1
    assert disk.id_ == 2


def test_disks_remembers_old_db_index(tmp_path):
    CONFIG1: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/foo/
            -
                path: ~/Downloads/bar/
    """

    CONFIG2: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/bar/
    """

    config.load_stream('', StringIO(CONFIG1))
    config.load_stream('', StringIO(CONFIG2))
    config.load_stream('', StringIO(CONFIG1))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.disk_name == 'foo'
    assert disk.index_ == 1
    assert disk.id_ == 3

    disk = disks[1]

    assert disk.disk_name == 'bar'
    assert disk.index_ == 2
    assert disk.id_ == 2


def test_disk_enabled_by_default(tmp_path):
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
    """
    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG))

    disks = dal.session.query(Disk)

    assert disks.count() == 1

    disk = disks.one()

    assert disk.checked is True


def test_disk_remembers_enabled_state(tmp_path):
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
    """
    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG))

    disk = dal.session.query(Disk).one()
    disk.checked = False
    dal.session.commit()

    config.load_stream(config_file, StringIO(CONFIG))

    disk = dal.session.query(Disk).one()
    assert disk.checked is False


def test_remove_folders_on_deleted_disks(tmp_path):
    PATH_NAME1: Final[str] = 'foo1'
    PATH_NAME2: Final[str] = 'foo2'

    CONFIG1: Final[str] = f"""
        disks:
            -
                path: {tmp_path}/{PATH_NAME1}/
            -
                path: {tmp_path}/{PATH_NAME2}/
    """

    CONFIG2: Final[str] = f"""
        disks:
            -
                path: {tmp_path}/{PATH_NAME2}/
    """

    config_file = tmp_path / 'test.yml'
    config.load_stream(config_file, StringIO(CONFIG1))

    session = dal.session

    disk1 = session.query(Disk).filter(Disk.disk_name == PATH_NAME1).one()
    disk2 = session.query(Disk).filter(Disk.disk_name == PATH_NAME2).one()

    session.add(Folder(disk=disk1, folder_parent='.', folder_name='xxx', system_id='1'))
    session.add(Folder(disk=disk2, folder_parent='.', folder_name='xxx', system_id='1'))
    session.commit()

    config.load_stream(config_file, StringIO(CONFIG2))

    folders = session.query(Folder).all()

    assert len(folders) == 1

    folder = folders[0]

    assert folder.disk.disk_name == PATH_NAME2
