import functools
import re
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import dateutil.parser
import markdownify
import requests
import yaml
from bs4 import BeautifulSoup
from PIL import Image

from tutcatalogpy.common.tutorial_data import TutorialData


class block(str):
    def __new__(cls, value):
        o = (
            value
            .replace('\u2013', '--')
            .replace('\u2014', '--')
            .replace('\u2019', "'")
        )
        o = re.sub(r'\n\s*\n', '\n\n', o)
        o = re.sub(r'[\t ]*\n', '\n', o)
        return str.__new__(cls, o)


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

    MAX_IMAGE_WIDTH = 300
    IMAGE_EXT = 'JPEG'
    COVER_FILE = 'cover.jpg'
    COVER_HINT = 'cover'

    @dataclass
    class Error:
        file: str
        line: int
        message: str

    class store_exceptions:
        def __init__(self, func) -> None:
            functools.update_wrapper(self, func)
            self.func = func

        def __get__(self, instance, owner):
            return type(self)(self.func.__get__(instance, owner))

        def __call__(self, *args, **kwargs):
            try:
                self.func(*args, **kwargs)
            except Exception as ex:
                scrapper = self.func.__self__
                exc_tb = sys.exc_info()[2]
                exc_file = traceback.extract_tb(exc_tb)[-1][0]
                exc_line = traceback.extract_tb(exc_tb)[-1][1]
                scrapper.errors.append(Scrapper.Error(exc_file, exc_line, str(ex)))

    def __init__(self, publisher: str, publisher_name: str, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        self.source = source
        self.with_images = images
        self.verbose = verbose

        self.publisher = publisher_name
        self.url = url
        self.info = {}
        self.errors = []

        self.can_scrap = (publisher in location.split('.'))

        self.md = markdownify.MarkdownConverter(heading_style=markdownify.ATX, bullets='*')

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

    @staticmethod
    def download_image(url: str, filename: str) -> bool:
        r = requests.get(url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            im = Image.open(r.raw)
            im.thumbnail(size=(Scrapper.MAX_IMAGE_WIDTH, sys.maxsize), resample=Image.LANCZOS)
            im.save(filename, Scrapper.IMAGE_EXT)
            return True
        else:
            return False

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

    def get_info(self) -> None:
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
        if len(self.errors):
            description = self.info.get(self.DESCRIPTION_TAG, '')
            separator = '<div style="background-color:red">&nbsp;</div>\n'

            text = separator + '\n# PARSING ERRORS\n\n'
            err: Scrapper.Error
            for err in self.errors:
                text += f'* {err.message} [[{Path(err.file).name}:{err.line}]({err.file}:{err.line})]\n'
            text += '\n' + separator
            if len(description):
                text += '\n' + description

            self.info[self.DESCRIPTION_TAG] = block(text)

        return yaml.dump(self.info, sort_keys=False)
