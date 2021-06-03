from io import StringIO
from pathlib import Path
from typing import Final

import pytest

from tutcatalogpy.catalog.config import config
from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk


def test_empty_config():
    config.load_stream('', StringIO(''))
    assert dal.session is not None


def test_cache_set_to_sqlite_by_default():
    config.load_stream('', StringIO(''))
    assert dal.url == 'sqlite:///:memory:'


def test_sqlite_cache_without_path_raises():
    with pytest.raises(RuntimeError) as excinfo:
        config.load_stream('', StringIO("""
            cache:
                type: sqlite
        """))
    assert str(excinfo.value) == 'cache path not set'


def test_sqlite_cache_with_implicit_path(tmp_path):
    config.load_stream(tmp_path / 'foo.yml', StringIO("""
        cache:
            type: sqlite
    """))
    assert dal.url == f'sqlite:///{tmp_path}/foo.db'


def test_sqlite_cache_with_explicit_path(tmp_path):
    config.load_stream(tmp_path / 'foo.yml', StringIO(f"""
        cache:
            type: sqlite
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


def test_load_config_with_one_disk():
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
    """

    config.load_stream('', StringIO(CONFIG))

    disks = dal.session.query(Disk)

    assert disks.count() == 1

    disk = disks.one()

    assert disk.path_parent == str(Path('~/Downloads/').expanduser().absolute())
    assert disk.path_name == 'foo'
    assert disk.role == Disk.Role.UPLOADS
    assert disk.monitored is True
    assert disk.depth == 0
    assert disk.location == Disk.Location.LOCAL
    assert disk.id_ == 1
    assert disk.index_ == 0


def test_load_config_with_many_disk():
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    config.load_stream('', StringIO(CONFIG))

    disks = dal.session.query(Disk)

    assert disks.count() == 2

    disk = disks.offset(1).one()

    assert disk.path_parent == str(Path('~/Downloads/').expanduser().absolute())
    assert disk.path_name == 'bar'
    assert disk.role == Disk.Role.DEFAULT
    assert disk.monitored is False
    assert disk.depth == 2
    assert disk.location == Disk.Location.REMOTE
    assert disk.id_ == 2
    assert disk.index_ == 1


def test_reload_same_config_with_many_disk():
    CONFIG: Final[str] = """
        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    config.load_stream('', StringIO(CONFIG))
    config.load_stream('', StringIO(CONFIG))

    disks = dal.session.query(Disk).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.path_name == 'foo'
    assert disk.id_ == 1
    assert disk.index_ == 0

    disk = disks[1]

    assert disk.path_name == 'bar'
    assert disk.id_ == 2
    assert disk.index_ == 1


def test_reload_config_with_many_disk_updates_disk_index(tmp_path):
    CONFIG1: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    CONFIG2: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
    """

    config.load_stream('', StringIO(CONFIG1))
    config.load_stream('', StringIO(CONFIG2))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.path_name == 'bar'
    assert disk.index_ == 0
    assert disk.id_ == 2

    disk = disks[1]

    assert disk.path_name == 'foo'
    assert disk.index_ == 1
    assert disk.id_ == 1


def test_disks_removed_from_cache_when_removed_from_config(tmp_path):
    CONFIG1: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    CONFIG2: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    config.load_stream('', StringIO(CONFIG1))
    config.load_stream('', StringIO(CONFIG2))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 1

    disk = disks[0]

    assert disk.path_name == 'bar'
    assert disk.index_ == 0
    assert disk.id_ == 2


def test_disks_remembers_old_db_index(tmp_path):
    CONFIG1: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/foo/
                location: local
                role: uploads
                monitored: true
                depth: 0
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    CONFIG2: Final[str] = f"""
        cache:
            type: sqlite
            path: {tmp_path}/test.db

        disks:
            -
                path: ~/Downloads/bar/
                location: remote
                monitored: false
                depth: 2
    """

    config.load_stream('', StringIO(CONFIG1))
    config.load_stream('', StringIO(CONFIG2))
    config.load_stream('', StringIO(CONFIG1))

    disks = dal.session.query(Disk).order_by(Disk.index_).all()

    assert len(disks) == 2

    disk = disks[0]

    assert disk.path_name == 'foo'
    assert disk.index_ == 0
    assert disk.id_ == 3

    disk = disks[1]

    assert disk.path_name == 'bar'
    assert disk.index_ == 1
    assert disk.id_ == 2
