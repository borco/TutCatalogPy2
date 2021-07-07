from typing import List, Set, Tuple

from pytest import fixture, mark

# import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.common.db.dal import DataAccessLayer, dal
from tutcatalogpy.common.db.publisher import Publisher
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
        """, {('pub 1', 'lp 1', None, None), ('pub 1', 'lp 2', None, None)}),
        ("""
            publisher: pub 1
            learning_paths:
                -
                    name: lp 1
                    index: 10
                    show_in_title: yes
                - lp 2
        """, {('pub 1', 'lp 1', 10, True), ('pub 1', 'lp 2', None, None)})
    ]
)
def test_load_from_string_learning_paths_for_one_tutorial(text: str, learning_paths: Set[Tuple[str, str, str]], dal_: DataAccessLayer) -> None:
    tutorial = Tutorial()
    dal_.session.add(tutorial)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial, text)
    assert {(tlp.learning_path.publisher.name, tlp.learning_path.name, tlp.index, tlp.show_in_title) for tlp in tutorial.learning_paths} == learning_paths


@mark.parametrize(
    'text1, text2, publishers',
    [
        ('', '', [('', [])]),
        (
            """
                title: tut 1
                publisher: pub 1
                learning_paths:
                    - lp 1
                    - lp 2
            """,
            """
                title: tut 2
                publisher: pub 1
                learning_paths:
                    - lp 1
                    - lp 3
            """,
            [
                ('pub 1', [
                    ('lp 1', [('tut 1', None), ('tut 2', None)]),
                    ('lp 2', [('tut 1', None)]),
                    ('lp 3', [('tut 2', None)])
                ]),
            ]
        ),
        (
            """
                title: tut 1
                learning_paths:
                    - lp 1
                    - lp 2
            """,
            """
                title: tut 2
                publisher: pub 1
                learning_paths:
                    - lp 1
                    - lp 3
            """,
            [
                ('', [
                    ('lp 1', [('tut 1', None)]),
                    ('lp 2', [('tut 1', None)])
                ]),
                ('pub 1', [
                    ('lp 1', [('tut 2', None)]),
                    ('lp 3', [('tut 2', None)])
                ]),
            ]
        ),
    ],
)
def test_load_from_string_learning_paths_for_two_tutorials(text1: str, text2: str, publishers: List[Tuple[str, List[str]]], dal_: DataAccessLayer) -> None:
    tutorial1 = Tutorial()
    dal_.session.add(tutorial1)
    dal_.session.commit()

    tutorial2 = Tutorial()
    dal_.session.add(tutorial2)
    dal_.session.commit()

    TutorialData.load_from_string(dal_.session, tutorial1, text1)
    TutorialData.load_from_string(dal_.session, tutorial2, text2)

    pubs = []
    for pub in sorted(dal_.session.query(Publisher).all(), key=lambda p: p.name):
        lps = []
        for lp in sorted(pub.learning_paths, key=lambda lp: lp.name):
            tlps = sorted(lp.tutorials, key=lambda tlp: tlp.tutorial.title)
            lps.append((lp.name, [(tlp.tutorial.title, tlp.index) for tlp in tlps]))
        pubs.append((pub.name, lps))
    assert pubs == publishers
    # print('expected:\n', publishers)
    # print('actual:\n', pubs)
