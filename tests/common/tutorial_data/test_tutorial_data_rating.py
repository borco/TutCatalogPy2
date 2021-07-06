import fastjsonschema
from pytest import fixture, raises

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


def test_load_from_string_reads_rating(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, 'rating: 0')
    assert tutorial.rating == 0

    TutorialData.load_from_string(dal_.session, tutorial, 'rating: -5')
    assert tutorial.rating == -5

    TutorialData.load_from_string(dal_.session, tutorial, 'rating: 2')
    assert tutorial.rating == 2

    TutorialData.load_from_string(dal_.session, tutorial, 'rating: 5')
    assert tutorial.rating == 5

    TutorialData.load_from_string(dal_.session, tutorial, '')
    assert tutorial.rating == 0

    for text in ['rating: -6', 'rating: 6']:
        with raises(fastjsonschema.JsonSchemaValueException, match='^data.rating must .*'):
            TutorialData.load_from_string(dal_.session, tutorial, text)
