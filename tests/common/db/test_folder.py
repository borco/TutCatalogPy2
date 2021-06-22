from pathlib import Path

from pytest import fixture

from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.db.tutorial import Tutorial
import tutcatalogpy.common.logging_config  # noqa: F401


@fixture
def connection(tmp_path) -> str:
    return 'sqlite:///:memory:'
    # return f'sqlite:///{tmp_path}/test.db'


@fixture
def dal_(connection: str) -> DataAccessLayer:
    dal.connect(connection)
    yield dal
    dal.disconnect()


def test_create_folder(dal_: DataAccessLayer) -> None:
    folder = Folder(folder_parent='/my parent1/my parent2/', folder_name='my folder')
    dal_.session.add(folder)
    dal_.session.commit()

    dal_.renew_session()
    folders = dal_.session.query(Folder).all()

    assert len(folders) == 1

    folder: Folder = folders[0]
    assert folder.path() == Path('/my parent1/my parent2/my folder')


def test_connect_with_tutorial(dal_: DataAccessLayer) -> None:
    folder = Folder(folder_parent='/my parent1/my parent2/', folder_name='my folder')
    dal_.session.add(folder)
    dal_.session.commit()

    tutorial = Tutorial(title='my tutorial')
    folder.tutorial = tutorial
    dal_.session.commit()

    dal_.renew_session()
    folder: Folder = dal_.session.query(Folder).one()

    assert folder.tutorial.title == 'my tutorial'
