from typing import Set

from pytest import fixture, mark

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.author import Author
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
