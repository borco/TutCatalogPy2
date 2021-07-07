from pytest import fixture

from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.learning_path import LearningPath
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.db.tutorial_learning_path import TutorialLearningPath
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


def test_create_learning_path_without_publisher(dal_: DataAccessLayer) -> None:
    learning_path = LearningPath(name='my path')
    dal_.session.add(learning_path)
    dal_.session.commit()

    dal_.renew_session()
    learning_paths = dal_.session.query(LearningPath).all()

    assert len(learning_paths) == 1

    learning_path = learning_paths[0]

    assert learning_path.name == 'my path'
    assert learning_path.publisher is None


def test_create_learning_path_with_publisher(dal_: DataAccessLayer) -> None:
    learning_path = LearningPath(name='my path')
    publisher = Publisher(name='my publisher')
    learning_path.publisher = publisher
    dal_.session.add(learning_path)
    dal_.session.commit()

    dal_.renew_session()
    learning_path = dal_.session.query(LearningPath).one()

    assert learning_path.publisher is not None
    assert learning_path.publisher.name == 'my publisher'


def test_create_tutorial_with_learning_path(dal_: DataAccessLayer) -> None:
    tutorial = Tutorial(title='my tutorial')
    dal_.session.add(tutorial)
    dal_.session.commit()

    learning_path = LearningPath(name='my path')
    tlp = TutorialLearningPath(tutorial=tutorial, learning_path=learning_path, index=5)
    tutorial.learning_paths.append(tlp)
    dal_.session.commit()

    dal_.renew_session()
    learning_path = dal_.session.query(LearningPath).one()

    assert len(learning_path.tutorials) == 1

    tlp: TutorialLearningPath = learning_path.tutorials[0]

    assert tlp.tutorial.title == 'my tutorial'
    assert tlp.index == 5
