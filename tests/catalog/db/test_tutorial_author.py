from pytest import fixture

from tutcatalogpy.catalog.db.author import Author
from tutcatalogpy.catalog.db.dal import DataAccessLayer, dal
from tutcatalogpy.catalog.db.tutorial import Tutorial
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


def test_add_one_author(dal_: DataAccessLayer) -> None:
    author = Author(name='author')
    tutorial = Tutorial(title='tutorial')
    tutorial.authors.append(author)
    dal_.session.add(tutorial)
    dal_.session.commit()
    dal_.renew_session()

    tutorial = dal_.session.query(Tutorial).one()

    assert len(tutorial.authors) == 1
    assert tutorial.authors[0].name == 'author'


def test_add_two_authors(dal_: DataAccessLayer) -> None:
    author1 = Author(name='author1')
    author2 = Author(name='author2')
    tutorial = Tutorial(title='tutorial')
    tutorial.authors.append(author1)
    tutorial.authors.append(author2)
    dal_.session.add(tutorial)
    dal_.session.commit()
    dal_.renew_session()

    tutorial = dal_.session.query(Tutorial).one()

    assert len(tutorial.authors) == 2
    assert {author.name for author in tutorial.authors} == {'author1', 'author2'}


def test_remove_one_author(dal_: DataAccessLayer) -> None:
    author1 = Author(name='author1')
    author2 = Author(name='author2')
    tutorial = Tutorial(title='tutorial')
    tutorial.authors.append(author1)
    tutorial.authors.append(author2)
    dal_.session.add(tutorial)
    dal_.session.commit()
    dal_.renew_session()

    tutorial = dal_.session.query(Tutorial).one()
    some_author = dal_.session.query(Author).filter(Author.name == 'author1').one()
    tutorial.authors.remove(some_author)
    dal_.session.commit()
    dal_.renew_session()

    tutorial = dal_.session.query(Tutorial).one()
    assert len(tutorial.authors) == 1
    assert tutorial.authors[0].name == 'author2'
