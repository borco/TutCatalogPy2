from typing import Optional

from pytest import fixture
from sqlalchemy.orm.session import Session

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


def test_create_tutorial(dal_: DataAccessLayer) -> None:
    session: Optional[Session] = dal_.session
    tutorial = Tutorial(title='tutorial')
    session.add(tutorial)
    session.commit()
    id_ = tutorial.id_

    dal_.renew_session()
    session = dal_.session
    tutorial = session.query(Tutorial).one()

    assert tutorial.id_ == id_
