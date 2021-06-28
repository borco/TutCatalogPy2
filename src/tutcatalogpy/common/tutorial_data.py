import logging
from re import compile
from typing import Any, Dict, Final

import fastjsonschema
import yaml
from sqlalchemy.orm.session import Session

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.base import FIELD_SEPARATOR
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TutorialData:
    FILE_NAME: Final[str] = 'info.tc'

    PUBLISHER_KEY: Final[str] = 'publisher'
    TITLE_KEY: Final[str] = 'title'
    AUTHORS_KEY: Final[str] = 'author'
    RELEASED_KEY: Final[str] = 'released'
    DURATION_KEY: Final[str] = 'duration'
    LEVEL_KEY: Final[str] = 'level'
    RATING_KEY: Final[str] = 'rating'
    URL_KEY: Final[str] = 'url'
    COMPLETE_KEY: Final[str] = 'complete'
    VIEWED_KEY: Final[str] = 'viewed'
    STARTED_KEY: Final[str] = 'started'
    FINISHED_KEY: Final[str] = 'finished'
    TODO_KEY: Final[str] = 'todo'
    ONLINE_KEY: Final[str] = 'online'
    TAGS_KEY: Final[str] = 'tags'
    MY_TAGS_KEY: Final[str] = 'extraTags'
    LEARNING_PATHS_KEY: Final[str] = 'learning_paths'
    MY_LEARNING_PATHS_KEY: Final[str] = 'my_learning_paths'
    DESCRIPTION_KEY: Final[str] = 'description'

    RELEASED_MINIMUM_YEAR: Final[int] = 1900
    RELEASED_MAXIMUM_YEAR: Final[int] = 3000
    RELEASED_REGEX: Final[str] = r'^\d{4}(/\d{2}(/\d{2})?)?$'
    DURATION_REGEX: Final[str] = r'(^(?P<hours>\d{1,3})h)? *((?P<minutes>\d{1,2})m)?$'

    # fastjsonschema returns default values if no data is provided
    # https://horejsek.github.io/python-fastjsonschema/
    # https://json-schema.org/understanding-json-schema/index.html
    VALIDATION_SCHEMA: Final[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'publisher': {'type': 'string', 'default': ''},
            'title': {'type': 'string', 'default': ''},
            'author': {'type': 'array', 'items': {'type': 'string'}, 'default': ['']},
            'released': {
                'type': ['string', 'integer'],
                'pattern': RELEASED_REGEX,
                'minimum': RELEASED_MINIMUM_YEAR,
                'maximum': RELEASED_MAXIMUM_YEAR,
                'default': ''
            },
            'duration': {
                'type': 'string',
                'pattern': DURATION_REGEX,
                'default': ''
            }
        }
    }

    __validate = fastjsonschema.compile(VALIDATION_SCHEMA)
    __duration_regex: Final = compile(DURATION_REGEX)

    @staticmethod
    def load_from_string(session: Session, tutorial: Tutorial, text: str) -> None:
        if len(text) == 0:
            data = TutorialData.__validate({})
        else:
            data = yaml.load(text, Loader=yaml.FullLoader)
            if data is None:
                log.warning("Couldn't parse .tc file")
            data = TutorialData.__validate(data)

        assert session is not None
        assert tutorial is not None

        tutorial.title = str(data.get(TutorialData.TITLE_KEY))

        publisher_name = str(data.get(TutorialData.PUBLISHER_KEY))
        publisher = session.query(Publisher).filter_by(name=publisher_name).first()
        if publisher is None:
            publisher = Publisher(name=publisher_name)
        tutorial.publisher = publisher

        all_authors = []
        for name in data.get(TutorialData.AUTHORS_KEY):
            author = session.query(Author).filter_by(name=name).first()
            if author is None:
                author = Author(name=name)
            tutorial.authors.append(author)
            all_authors.append(author.name)
        all_authors.sort()
        tutorial.all_authors = FIELD_SEPARATOR.join([''] + all_authors + [''])

        tutorial.released = data.get(TutorialData.RELEASED_KEY)

        tutorial.duration = TutorialData.parse_duration(data.get(TutorialData.DURATION_KEY))

    @staticmethod
    def parse_duration(text: str) -> int:
        match = TutorialData.__duration_regex.match(text)
        if match is not None:
            h = match['hours']
            m = match['minutes']
            h = int(h) if h is not None else 0
            m = int(m) if m is not None else 0
            return h * 60 + m
        else:
            # fastjsonschema doesn't correctly
            raise fastjsonschema.JsonSchemaValueException('data.duration must match ' + TutorialData.DURATION_REGEX)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
