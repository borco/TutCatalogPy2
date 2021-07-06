from typing import Set, Tuple

from pytest import fixture, mark

# import tutcatalogpy.common.logging_config  # noqa: F401
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
    'text, learning_paths',
    [
        ('', set()),
        ("""
            publisher: pub 1
            learning_paths:
                - lp 1
                - lp 2
        """, {('pub 1', 'lp 1', None), ('pub 1', 'lp 2', None)})
    ]
)
def test_load_from_string_reads_learning_paths(text: str, learning_paths: Set[Tuple[str, str, str]], dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    assert {(tlp.learning_path.publisher.name, tlp.learning_path.name, tlp.index) for tlp in tutorial.learning_paths} == learning_paths
