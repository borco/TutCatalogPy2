import fastjsonschema
from pytest import fixture, mark, raises

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


@mark.parametrize(
    'text, duration',
    [
        ('', 0),
        ('0m', 0),
        ('1m', 1),
        ('59m', 59),
        ('1h', 60),
        ('10h', 600),
        ('100h', 6000),
        ('1h 1m', 61),
        ('10h  1m', 601),
        ('10h     1m', 601),
        ('0s', 0),
        ('30s', 0),
        ('31s', 1),
        ('59s', 1),
    ]
)
def test_text_to_duration(text: str, duration: int) -> None:
    assert TutorialData.text_to_duration(text) == duration


@mark.parametrize(
    'text, duration',
    [
        ('', 0),
        ('duration: 0m', 0),
        ('duration: 00m', 0),
        ('duration: 1m', 1),
        ('duration: 01m', 1),
        ('duration: 59m', 59),
        ('duration: 1h', 60),
        ('duration: 10h', 600),
        ('duration: 100h', 6000),
        ('duration: 1h 0m', 60),
        ('duration: 1h 0m', 60),
        ('duration: 1h 1m', 61),
        ('duration: 1h 01m', 61),
        ('duration: 10h  1m', 601),
    ]
)
def test_load_from_string_reads_duration(text: str, duration: int, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.duration == duration


@mark.parametrize(
    'text',
    [
        'duration: 1',
        'duration: m',
        'duration: 111m',
        'duration: 60s',
    ]
)
def test_load_from_string_detects_invalid_duration(text: str, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    with raises(fastjsonschema.JsonSchemaValueException, match='^data.duration must .*'):
        TutorialData.load_from_string(dal_.session, tutorial, text)


@mark.parametrize(
    'duration, text',
    [
        (0, ''),
        (1, '1m'),
        (59, '59m'),
        (60, '1h 00m'),
        (600, '10h 00m'),
        (6000, '100h 00m'),
        (61, '1h 01m'),
        (601, '10h 01m'),
    ]
)
def test_duration_to_text(duration: int, text: str) -> None:
    assert TutorialData.duration_to_text(duration) == text
