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


def test_purge_authors_without_tutorials(dal_: DataAccessLayer) -> None:
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
    dal_.remove_authors_without_tutorials()

    dal_.renew_session()
    authors = dal_.session.query(Author).all()

    assert len(authors) == 1
    assert authors[0].name == 'author2'


def test_purge_authors_without_tutorials_2(dal_: DataAccessLayer) -> None:
    tutorial1 = Tutorial(title='tutorial1')
    tutorial2 = Tutorial(title='tutorial2')

    author1 = Author(name='author1')
    author2 = Author(name='author2')
    author3 = Author(name='author3')
    author4 = Author(name='author4')

    tutorial1.authors.append(author1)
    tutorial1.authors.append(author2)

    tutorial2.authors.append(author1)
    tutorial2.authors.append(author3)
    tutorial2.authors.append(author4)

    dal_.session.add(tutorial1)
    dal_.session.add(tutorial2)
    dal_.session.commit()

    dal_.renew_session()
    tutorial1 = dal_.session.query(Tutorial).filter_by(title='tutorial1').one()
    tutorial2 = dal_.session.query(Tutorial).filter_by(title='tutorial2').one()
    author1 = dal_.session.query(Author).filter_by(name='author1').one()
    author2 = dal_.session.query(Author).filter_by(name='author2').one()
    tutorial1.authors.remove(author1)
    tutorial1.authors.remove(author2)
    tutorial2.authors.remove(author1)
    dal_.session.commit()

    dal_.renew_session()
    dal_.remove_authors_without_tutorials()

    dal_.renew_session()
    tutorial1 = dal_.session.query(Tutorial).filter_by(title='tutorial1').one()
    tutorial2 = dal_.session.query(Tutorial).filter_by(title='tutorial2').one()
    authors = dal_.session.query(Author).all()

    assert len(authors) == 2
    assert {author.name for author in authors} == {'author3', 'author4'}

    assert tutorial1.authors == []
    assert {author.name for author in tutorial2.authors} == {'author3', 'author4'}
