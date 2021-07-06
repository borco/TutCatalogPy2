from pytest import fixture, mark

from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.tag import Tag
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


@mark.parametrize(
    'name, source',
    [
        ('publisher tag', Tag.Source.PUBLISHER),
        ('personal tag', Tag.Source.PERSONAL),
    ]
)
def test_add_one_tag(name: str, source: Tag.Source, dal_: DataAccessLayer) -> None:
    tag = Tag(name=name, source=source)
    tutorial = Tutorial(title='tutorial')
    tutorial.tags.append(tag)
    dal_.session.add(tutorial)
    dal_.session.commit()
    dal_.renew_session()

    tutorial = dal_.session.query(Tutorial).one()

    assert len(tutorial.tags) == 1
    assert tutorial.tags[0].name == name
    assert tutorial.tags[0].source == source
