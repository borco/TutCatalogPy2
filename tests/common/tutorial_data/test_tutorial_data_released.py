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
    'text, released',
    [
        ('', ''),
        ('released: 2000', '2000'),
        ('released: 2000/01', '2000/01'),
        ('released: 2000/01/01', '2000/01/01'),
    ]
)
def test_load_from_string_reads_released(text: str, released: str, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    dal_.session.commit()

    dal_.renew_session()
    tutorial = dal_.session.query(Tutorial).one()
    assert tutorial.released == released


@mark.parametrize(
    'text',
    [
        # verify integer values
        'released: 1899',
        'released: 3001',
        # 'released: 2000.', # we can't test for this, as it will be interpretted as an integer
        # verify string values
        'released: x',
        'released: 2000/1',
        'released: 2000/01/1',
    ]
)
def test_load_from_string_detects_invalid_released(text: str) -> None:
    with raises(fastjsonschema.JsonSchemaValueException, match='^data.released must .*'):
        TutorialData.load_from_string(None, None, text)
