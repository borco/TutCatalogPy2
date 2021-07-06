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


def test_load_from_string_sets_title(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'title: my title')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.title == 'my title'


def test_load_from_empty_string_unsets_title(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial(title='my title')
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, '')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.title == ''


def test_load_from_string_unsets_title(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial(title='my title')
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'publisher: my publisher')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.title == ''
