from pathlib import Path

from pytest import fixture

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.scan_worker import ScanWorker
from tutcatalogpy.common.tutorial_data import TutorialData


@fixture
def connection(tmp_path: Path) -> str:
    return 'sqlite:///:memory:'
    # return f'sqlite:///{tmp_path}/test.db'


@fixture
def dal_(connection: str) -> DataAccessLayer:
    dal.connect(connection)
    yield dal
    dal.disconnect()


def test_update_folder_tutorial_without_info_tc(tmp_path: Path, dal_: DataAccessLayer) -> None:
    folder = Folder(folder_parent=str(tmp_path.parent), folder_name=str(tmp_path.name))
    dal_.session.add(folder)
    dal_.session.commit()

    dal_.renew_session()
    folder = dal_.session.query(Folder).one()
    ScanWorker.update_folder_tutorial(dal_.session, folder)

    assert folder.tutorial is None


def test_update_folder_tutorial_after_removing_info_tc(tmp_path: Path, dal_: DataAccessLayer) -> None:
    folder = Folder(folder_parent=str(tmp_path.parent), folder_name=str(tmp_path.name))
    tutorial = Tutorial(title='my tutorial')
    folder.tutorial = tutorial
    dal_.session.add(folder)
    dal_.session.commit()

    dal_.renew_session()
    folder = dal_.session.query(Folder).one()
    ScanWorker.update_folder_tutorial(dal_.session, folder)

    assert folder.tutorial is None


def test_update_folder_tutorial_from_empty_info_tc(tmp_path: Path, dal_: DataAccessLayer) -> None:
    info_tc = tmp_path / TutorialData.FILE_NAME
    info_tc.touch()

    folder = Folder(folder_parent=str(tmp_path.parent), folder_name=str(tmp_path.name))
    dal_.session.add(folder)
    dal_.session.commit()

    dal_.renew_session()
    folder = dal_.session.query(Folder).one()
    ScanWorker.update_folder_tutorial(dal_.session, folder)

    assert folder.tutorial is not None
    assert folder.tutorial.title == ''
    assert folder.tutorial.size == 0


def test_update_folder_tutorial_from_invalid_info_tc(tmp_path: Path, dal_: DataAccessLayer) -> None:
    info_tc = tmp_path / TutorialData.FILE_NAME
    with open(info_tc, 'w') as f:
        f.write('invalid yaml')

    folder = Folder(folder_parent=str(tmp_path.parent), folder_name=str(tmp_path.name))
    dal_.session.add(folder)
    dal_.session.commit()

    dal_.renew_session()
    folder = dal_.session.query(Folder).one()
    ScanWorker.update_folder_tutorial(dal_.session, folder)

    assert folder.tutorial is None
