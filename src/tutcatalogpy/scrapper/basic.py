from datetime import datetime

import dateutil.parser
import yaml
from bs4 import BeautifulSoup

from tutcatalogpy.common.tutorial_data import TutorialData


class block(str):
    pass


def block_representer(dumper, data):
    style = '|'
    tag = u'tag:yaml.org,2002:str'
    return dumper.represent_scalar(tag, data, style=style)


yaml.add_representer(block, block_representer)


class Scrapper:
    PUBLISHER_TAG = 'publisher'
    TITLE_TAG = 'title'
    AUTHORS_TAG = 'author'
    RELEASED_TAG = 'released'
    DURATION_TAG = 'duration'
    LEVEL_TAG = 'level'
    URL_TAG = 'url'
    TAGS_TAG = 'tags'
    DESCRIPTION_TAG = 'description'

    def __init__(self, publisher: str, publisher_name: str, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        self.url = url
        self.source = source
        self.download_images = images
        self.verbose = verbose
        self.publisher = publisher_name
        self.info = {}
        self.can_scrap = (publisher in location.split('.'))

    @staticmethod
    def secs_to_duration(value: int) -> str:
        return TutorialData.duration_to_text(value // 60)

    @staticmethod
    def parse_date(value: str) -> datetime:
        return dateutil.parser.parse(value, None, tzinfos={'EDT': 0})

    @staticmethod
    def valid_fs_name(value: str) -> str:
        """Return a string that can be used as a filename component."""
        return value.replace(':', ' -').strip()

    @staticmethod
    def italic(value: str) -> str:
        return f'*{value}*'

    @staticmethod
    def h(level: int, value: str) -> str:
        return f"{'#' * level} {value}\n\n"

    def get_title(self) -> None:
        pass

    def get_authors(self) -> None:
        pass

    def get_released(self) -> None:
        pass

    def get_duration(self) -> None:
        pass

    def get_level(self) -> None:
        pass

    def get_tags(self) -> None:
        pass

    def get_description(self) -> None:
        pass

    def get_images(self) -> None:
        pass

    def get_info(self) -> None:
        if self.download_images:
            self.get_images()

        self.info[self.PUBLISHER_TAG] = self.publisher
        self.get_title()
        self.get_authors()
        self.get_released()
        self.get_duration()
        self.get_level()
        self.info[self.URL_TAG] = self.url
        self.get_tags()
        self.get_description()

    def scrap(self) -> None:
        if self.verbose:
            print(f'Using {__name__} scrapper')
        self.soup = BeautifulSoup(self.source, 'html.parser')
        self.get_info()

    def dump(self):
        return yaml.dump(self.info, sort_keys=False)
