import logging
from typing import Any, Dict, Final

import fastjsonschema
import yaml
from sqlalchemy.orm.session import Session

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

    VALIDATION_SCHEMA: Final[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string', 'default': ''},
            'publisher': {'type': 'string', 'default': ''},
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
