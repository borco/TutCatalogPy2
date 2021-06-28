import logging
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
                'pattern': r'^\d{4}(/\d{2}(/\d{2})?)?$',
                'minimum': 1900,
                'maximum': 3000,
                'default': ''
            },
        }
    }

    validate = fastjsonschema.compile(VALIDATION_SCHEMA)

    @staticmethod
    def load_from_string(session: Session, tutorial: Tutorial, text: str) -> None:
        if len(text) == 0:
            data = TutorialData.validate({})
        else:
            data = yaml.load(text, Loader=yaml.FullLoader)
            if data is None:
                data = TutorialData.validate(data)
                log.warning('Could not parse .tc file')
            else:
                data = TutorialData.validate(data)

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


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
