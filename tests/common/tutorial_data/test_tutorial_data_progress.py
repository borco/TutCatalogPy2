from pytest import fixture, mark

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
    'text, progress',
    [
        ('', Tutorial.Progress.NOT_STARTED),
        ('viewed: no', Tutorial.Progress.NOT_STARTED),
        ('progress: not started', Tutorial.Progress.NOT_STARTED),
        ('progress: started', Tutorial.Progress.STARTED),
        ('progress: finished', Tutorial.Progress.FINISHED),
        ('viewed: no\nprogress: finished', Tutorial.Progress.FINISHED),
        ('viewed: yes\nprogress: not started', Tutorial.Progress.NOT_STARTED),
        ('viewed: yes\nprogress: started', Tutorial.Progress.STARTED),
    ]
)
def test_load_from_string_reads_progress(text, progress, dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    assert tutorial.progress == progress.value
