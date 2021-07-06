from pytest import fixture

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.tutorial_data import TutorialData


@fixture
def connection(tmp_path) -> str:
    return 'sqlite:///:memory:'
    # return f'sqlite:///{tmp_path}/test.db'


@fixture
def dal_(connection: str) -> DataAccessLayer:
    dal.connect(connection)
    yield dal
    dal.disconnect()


def test_load_from_string_reads_complete(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'complete: yes')
    assert tutorial.is_complete is True

    TutorialData.load_from_string(dal_.session, tutorial, 'complete: no')
    assert tutorial.is_complete is False

    TutorialData.load_from_string(dal_.session, tutorial, '')
    assert tutorial.is_complete is True


def test_load_from_string_reads_online(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'online: yes')
    assert tutorial.is_online is True

    TutorialData.load_from_string(dal_.session, tutorial, 'online: no')
    assert tutorial.is_online is False

    TutorialData.load_from_string(dal_.session, tutorial, '')
    assert tutorial.is_online is False


def test_load_from_string_reads_todo(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'todo: yes')
    assert tutorial.todo is True

    TutorialData.load_from_string(dal_.session, tutorial, 'todo: no')
    assert tutorial.todo is False

    TutorialData.load_from_string(dal_.session, tutorial, '')
    assert tutorial.todo is False
