import enum
import logging
from re import compile
from typing import Any, Dict, Final, List

import fastjsonschema
import yaml
from sqlalchemy.orm.session import Session

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.base import FIELD_SEPARATOR
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tag import Tag
from tutcatalogpy.common.db.tutorial import Tutorial

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TutorialLevel(enum.IntFlag):
    UNKNOWN = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 4
    ANY = BEGINNER | INTERMEDIATE | ADVANCED


TEXT_TO_TUTORIAL_LEVEL: Final[Dict[str, TutorialLevel]] = {
    '': TutorialLevel.UNKNOWN,
    'beginner': TutorialLevel.BEGINNER,
    'intermediate': TutorialLevel.INTERMEDIATE,
    'advanced': TutorialLevel.ADVANCED,
    'any': TutorialLevel.ANY,
}

TUTORIAL_LEVEL_TO_TEXT: Final[Dict[TutorialLevel, str]] = {
    TutorialLevel.UNKNOWN: '',
    TutorialLevel.BEGINNER: 'beginner',
    TutorialLevel.INTERMEDIATE: 'intermediate',
    TutorialLevel.ADVANCED: 'advanced',
    TutorialLevel.ANY: 'any',
}


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
    IS_COMPLETE_KEY: Final[str] = 'complete'
    VIEWED_KEY: Final[str] = 'viewed'
    PROGRESS_KEY: Final[str] = 'progress'
    TODO_KEY: Final[str] = 'todo'
    IS_ONLINE_KEY: Final[str] = 'online'
    LEGACY_TAGS_KEY: Final[str] = 'tags'
    LEGACY_EXTRA_TAGS_KEY: Final[str] = 'extraTags'
    PUBLISHER_TAGS_KEY: Final[str] = 'publisher_tags'
    PERSONAL_TAGS_KEY: Final[str] = 'personal_tags'
    LEARNING_PATHS_KEY: Final[str] = 'learning_paths'
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
            PUBLISHER_KEY: {'type': 'string', 'default': ''},
            TITLE_KEY: {'type': 'string', 'default': ''},
            AUTHORS_KEY: {'type': 'array', 'items': {'type': 'string'}, 'default': ['']},
            RELEASED_KEY: {
                'type': ['string', 'integer'],
                'pattern': RELEASED_REGEX,
                'minimum': RELEASED_MINIMUM_YEAR,
                'maximum': RELEASED_MAXIMUM_YEAR,
                'default': ''
            },
            DURATION_KEY: {
                'type': 'string',
                'pattern': DURATION_REGEX,
                'default': ''
            },
            LEVEL_KEY: {'type': 'string', 'default': ''},
            URL_KEY: {'type': 'string', 'default': ''},
            IS_COMPLETE_KEY: {'type': 'boolean', 'default': True},
            IS_ONLINE_KEY: {'type': 'boolean', 'default': False},
            TODO_KEY: {'type': 'boolean', 'default': False},
            VIEWED_KEY: {'type': 'boolean', 'default': False},
            PROGRESS_KEY: {'enum': [x.label for x in Tutorial.Progress], 'default': None},
            RATING_KEY: {'enum': [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5], 'default': 0},
            LEGACY_TAGS_KEY: {'type': 'array', 'items': {'type': 'string'}, 'default': []},
            LEGACY_EXTRA_TAGS_KEY: {'type': 'array', 'items': {'type': 'string'}, 'default': []},
            PUBLISHER_TAGS_KEY: {'type': 'array', 'items': {'type': 'string'}, 'default': []},
            PERSONAL_TAGS_KEY: {'type': 'array', 'items': {'type': 'string'}, 'default': []},
            DESCRIPTION_KEY: {'type': 'string', 'default': ''},
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

        TutorialData.set_publisher(session, tutorial, data.get(TutorialData.PUBLISHER_KEY))

        TutorialData.set_authors(session, tutorial, data.get(TutorialData.AUTHORS_KEY))

        tutorial.released = data.get(TutorialData.RELEASED_KEY)

        tutorial.duration = TutorialData.text_to_duration(data.get(TutorialData.DURATION_KEY))

        tutorial.level = TutorialData.text_to_level(data.get(TutorialData.LEVEL_KEY))

        tutorial.is_complete = data.get(TutorialData.IS_COMPLETE_KEY)

        tutorial.is_online = data.get(TutorialData.IS_ONLINE_KEY)

        tutorial.todo = data.get(TutorialData.TODO_KEY)

        tutorial.progress = TutorialData.parse_progress(data.get(TutorialData.VIEWED_KEY), data.get(TutorialData.PROGRESS_KEY))

        tutorial.rating = data.get(TutorialData.RATING_KEY)

        tutorial.url = data.get(TutorialData.URL_KEY)

        TutorialData.add_tags(session, tutorial, data.get(TutorialData.LEGACY_TAGS_KEY), Tag.Source.PUBLISHER)
        TutorialData.add_tags(session, tutorial, data.get(TutorialData.PUBLISHER_TAGS_KEY), Tag.Source.PUBLISHER)

        TutorialData.add_tags(session, tutorial, data.get(TutorialData.LEGACY_EXTRA_TAGS_KEY), Tag.Source.PERSONAL)
        TutorialData.add_tags(session, tutorial, data.get(TutorialData.PERSONAL_TAGS_KEY), Tag.Source.PERSONAL)

        tutorial.description = data.get(TutorialData.DESCRIPTION_KEY)

    @staticmethod
    def set_publisher(session: Session, tutorial: Tutorial, text: str) -> None:
        publisher = session.query(Publisher).filter_by(name=text).first()
        if publisher is None:
            publisher = Publisher(name=text)
        tutorial.publisher = publisher

    @staticmethod
    def set_authors(session: Session, tutorial: Tutorial, names: List[str]) -> None:
        all_authors = []
        for name in names:
            author = session.query(Author).filter_by(name=name).first()
            if author is None:
                author = Author(name=name)
            tutorial.authors.append(author)
            all_authors.append(author.name)
        all_authors.sort()
        tutorial.all_authors = FIELD_SEPARATOR.join([''] + all_authors + [''])

    @staticmethod
    def add_tags(session: Session, tutorial: Tutorial, names: List[str], source: Tag.Source) -> None:
        new_tags = []
        for name in names:
            if len(name) == 0:
                continue
            tag = session.query(Tag).filter_by(name=name, source=source).first()
            if tag is None:
                tag = Tag(name=name, source=source)
            tutorial.tags.append(tag)
            new_tags.append(f'{tag.name}|{tag.source}')
        if len(new_tags) > 0:
            new_tags += str(tutorial.all_tags).split(FIELD_SEPARATOR)[1:-1]
            new_tags = list(set(new_tags))
            new_tags.sort()
            tutorial.all_tags = FIELD_SEPARATOR.join([''] + new_tags + [''])

    @staticmethod
    def parse_progress(viewed: str, progress: str) -> int:
        value: int = Tutorial.Progress.FINISHED.value if viewed else Tutorial.Progress.NOT_STARTED.value
        if progress is not None:
            p = next((x for x in list(Tutorial.Progress) if x.label == progress), None)
            if p is not None:
                value = p.value
        return value

    @staticmethod
    def text_to_duration(text: str) -> int:
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

    @staticmethod
    def duration_to_text(minutes: int) -> str:
        if minutes == 0:
            return ''
        hours = minutes // 60
        minutes %= 60
        return f'{hours}h {minutes:02}m' if hours > 0 else f'{minutes}m'

    @staticmethod
    def text_to_level(text: str) -> TutorialLevel:
        level = TutorialLevel.UNKNOWN
        for token in map(str.strip, text.split(',')):
            lvl = TEXT_TO_TUTORIAL_LEVEL.get(token, None)
            if lvl is not None:
                level |= lvl
        return level

    @staticmethod
    def level_to_text(level: TutorialLevel) -> str:
        if TutorialLevel.ANY & level == TutorialLevel.ANY:
            return TUTORIAL_LEVEL_TO_TEXT[TutorialLevel.ANY]

        tokens = []
        for lvl in [
            TutorialLevel.BEGINNER,
            TutorialLevel.INTERMEDIATE,
            TutorialLevel.ADVANCED
        ]:
            if level & lvl == lvl:
                tokens.append(TUTORIAL_LEVEL_TO_TEXT[lvl])
        return ', '.join(tokens)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
