from pytest import fixture, mark

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.tutorial_data import TutorialData, TutorialLevel


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
    'text, level',
    [
        ('', TutorialLevel.UNKNOWN),
        ('beginner', TutorialLevel.BEGINNER),
        ('intermediate', TutorialLevel.INTERMEDIATE),
        ('advanced', TutorialLevel.ADVANCED),
        ('any', TutorialLevel.ANY),
        ('intermediate, beginner', TutorialLevel.BEGINNER | TutorialLevel.INTERMEDIATE),
        ('intermediate, beginner, advanced', TutorialLevel.ANY),
        ('intermediate, advanced', TutorialLevel.INTERMEDIATE | TutorialLevel.ADVANCED),
        ('xxx', TutorialLevel.UNKNOWN),
        ('xxx, intermediate', TutorialLevel.INTERMEDIATE),
    ]
)
def test_text_to_level(text: str, level: TutorialLevel) -> None:
    assert TutorialData.text_to_level(text) == level


@mark.parametrize(
    'level, text',
    [
        (TutorialLevel.UNKNOWN, ''),
        (TutorialLevel.BEGINNER, 'beginner'),
        (TutorialLevel.INTERMEDIATE, 'intermediate'),
        (TutorialLevel.ADVANCED, 'advanced'),
        (TutorialLevel.ANY, 'any'),
        (TutorialLevel.BEGINNER | TutorialLevel.INTERMEDIATE, 'beginner, intermediate'),
        (TutorialLevel.INTERMEDIATE | TutorialLevel.ADVANCED, 'intermediate, advanced'),
    ]
)
def test_level_to_text(level: TutorialLevel, text: str) -> None:
    assert TutorialData.level_to_text(level) == text


@mark.parametrize(
    'level',
    [
        TutorialLevel.UNKNOWN,
        TutorialLevel.BEGINNER,
        TutorialLevel.INTERMEDIATE,
        TutorialLevel.ADVANCED,
        TutorialLevel.ANY,
        TutorialLevel.BEGINNER | TutorialLevel.INTERMEDIATE,
        TutorialLevel.INTERMEDIATE | TutorialLevel.ADVANCED,
    ]
)
def test_level_to_text_to_level(level: TutorialLevel) -> None:
    text = TutorialData.level_to_text(level)
    assert TutorialData.text_to_level(text) & level == level


@mark.parametrize(
    'text, level',
    [
        ('', TutorialLevel.UNKNOWN),
        ('level: beginner', TutorialLevel.BEGINNER),
        ('level: intermediate', TutorialLevel.INTERMEDIATE),
        ('level: advanced', TutorialLevel.ADVANCED),
        ('level: any', TutorialLevel.ANY),
        ('level: intermediate, beginner', TutorialLevel.BEGINNER | TutorialLevel.INTERMEDIATE),
        ('level: intermediate, beginner, advanced', TutorialLevel.ANY),
        ('level: intermediate, advanced', TutorialLevel.INTERMEDIATE | TutorialLevel.ADVANCED),
        ('level: xxx', TutorialLevel.UNKNOWN),
        ('level: xxx, intermediate', TutorialLevel.INTERMEDIATE),
    ]
)
def test_load_from_string_reads_level(text: str, level: TutorialLevel, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.level == level
