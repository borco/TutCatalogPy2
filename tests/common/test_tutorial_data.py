from pytest import fixture

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.publisher import Publisher
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


def test_load_from_string_sets_publisher(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'publisher: my publisher')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()

    assert tutorial.publisher is not None
    assert tutorial.publisher.name == 'my publisher'


def test_load_from_string_set_empty_publisher_if_none_specified(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'title: my title')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()

    assert tutorial.publisher is not None
    assert tutorial.publisher.name == ''


def test_load_from_empty_string_unsets_publisher(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    publisher = Publisher(name='my publisher')
    tutorial.publisher = publisher
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, '')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()

    assert tutorial.publisher.name == ''


def test_load_from_string_unsets_publisher(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    publisher = Publisher(name='my publisher')
    tutorial.publisher = publisher
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'title: my title')
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()

    assert tutorial.publisher.name == ''


def test_load_from_string_reuses_publisher(dal_: DataAccessLayer) -> None:
    publisher = Publisher(name='my publisher')
    dal_.session.add(publisher)
    dal_.session.commit()

    tutorial1 = Tutorial()
    tutorial2 = Tutorial()
    TutorialData.load_from_string(dal_.session, tutorial1, 'publisher: my publisher')
    TutorialData.load_from_string(dal_.session, tutorial2, 'publisher: my publisher')

    dal_.session.commit()

    dal_.renew_session()

    publishers = dal_.session.query(Publisher).all()
    assert len(publishers) == 1

    publisher = publishers[0]

    for tutorial in dal_.session.query(Tutorial):
        assert tutorial.publisher_id == publisher.id_
