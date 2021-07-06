from typing import List

from pytest import fixture, mark

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.tag import Tag
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
    'text, publisher_tags, personal_tags, all_tags',
    [
        ('', [], [], ''),
        ('tags: [foo, bar]', ['foo', 'bar'], [], ',bar|0,foo|0,'),
        ('publisher_tags: [foo, bar]', ['foo', 'bar'], [], ',bar|0,foo|0,'),
        ('extraTags: [foo, bar]', [], ['foo', 'bar'], ',bar|1,foo|1,'),
        ('personal_tags: [foo, bar]', [], ['foo', 'bar'], ',bar|1,foo|1,'),
        ('''
            tags: [bar, baz]
            extraTags: [foo, bar]
        ''', ['bar', 'baz'], ['foo', 'bar'], ',bar|0,bar|1,baz|0,foo|1,'),
        ('''
            publisher_tags: [bar, baz]
            personal_tags: [foo, bar]
        ''', ['bar', 'baz'], ['foo', 'bar'], ',bar|0,bar|1,baz|0,foo|1,'),
        ('''
            tags: [foo, bar]
            publisher_tags: [bar, baz]
            personal_tags: [foo, bar]
        ''', ['foo', 'bar', 'baz'], ['foo', 'bar'], ',bar|0,bar|1,baz|0,foo|0,foo|1,'),
    ]
)
def test_load_from_string_reads_tags(text: str, publisher_tags: List[str], personal_tags: List[str], all_tags: str, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)

    assert [tag.name for tag in dal_.session.query(Tag).filter_by(source=Tag.Source.PUBLISHER)] == publisher_tags
    assert [tag.name for tag in dal_.session.query(Tag).filter_by(source=Tag.Source.PERSONAL)] == personal_tags
    assert tutorial.all_tags == all_tags
