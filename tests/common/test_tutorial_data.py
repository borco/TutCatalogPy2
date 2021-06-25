from typing import Set

from pytest import fixture, mark

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.author import Author
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


@mark.parametrize(
    'text, authors',
    [
        ('', {''}),
        ('author: [Some Author]', {'Some Author'}),
        ('author: [Author 1, Author 2]', {'Author 1', 'Author 2'}),
    ]
)
def test_load_from_string_sets_author(dal_: DataAccessLayer, text: str, authors: Set[str]) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert {author.name for author in tutorial.authors} == authors


def test_load_from_string_authors_reused(dal_: DataAccessLayer) -> None:
    tutorial1 = Tutorial()
    tutorial2 = Tutorial()
    tutorial3 = Tutorial()
    dal_.session.add(tutorial1)
    dal_.session.add(tutorial2)
    dal_.session.add(tutorial3)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial1, '')
    TutorialData.load_from_string(dal_.session, tutorial2, 'author: [Author 1, Author 3]')
    TutorialData.load_from_string(dal_.session, tutorial3, 'author: [Author 2, Author 1]')
    dal_.session.commit()

    dal_.renew_session()
    authors = dal_.session.query(Author).all()

    assert len(authors) == 4
    assert {author.name for author in authors} == {'', 'Author 1', 'Author 2', 'Author 3'}
