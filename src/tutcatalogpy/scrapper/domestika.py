import json
import re
from typing import Optional, Union

import markdownify as md
from bs4.element import Tag, NavigableString

from tutcatalogpy.scrapper.basic import block, Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('domestika', 'Domestika', location, url, source, images, verbose)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
