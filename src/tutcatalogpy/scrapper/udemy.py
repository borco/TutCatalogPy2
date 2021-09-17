import json
import re
from typing import Optional, Union

from bs4.element import Tag, NavigableString

from tutcatalogpy.scrapper.basic import block, Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('udemy', 'Udemy', location, url, source, images, verbose)

    def get_data_purpose(self, tag, purpose) -> Optional[Union[Tag, NavigableString]]:
        return self.soup.find(tag, attrs={'data-purpose': purpose})

    def get_data_component_props(self, class_: str) -> Optional[dict]:
        div = self.soup.find('div', class_)
        if div:
            return json.loads(div['data-component-props'])
        return None

    @BasicScrapper.store_exceptions
    def get_title(self) -> None:
        title = self.get_data_purpose('h1', 'lead-title')
        if title and title.string:
            self.info[self.TITLE_TAG] = self.valid_fs_name(title.string)

    @BasicScrapper.store_exceptions
    def get_authors(self) -> None:
        authors = []
        a_tags = self.get_data_purpose('div', 'instructor-name-top').find_all('a')
        for a_tag in a_tags:
            name = a_tag.span.string.strip()
            if name:
                authors.append(name)
        if len(authors):
            self.info[self.AUTHORS_TAG] = authors

    @staticmethod
    def parse_released(value: str) -> str:
        """
        >>> s = Scrapper
        >>> s.parse_released("\\n\\n  Published 8/2016")
        '2016/08'
        >>> s.parse_released("2017-05-30T16:24:30Z")
        '2017/05'
        >>> s.parse_released('\\n\\nLast updated 7/2021\\n\\n')
        '2021/07'
        """
        r = re.compile(r'\s*(Published|Last updated)*\s*([^<]*)')
        m = r.match(value)
        if m is not None and len(m.groups()) == 2:
            value = m.groups()[1]
        return Scrapper.parse_date(value).strftime('%Y/%m')

    @BasicScrapper.store_exceptions
    def get_released(self) -> None:
        div = self.get_data_purpose('div', 'last-update-date')
        if div:
            span = div.find_all('span')[-1]
            if span:
                released = self.parse_released(span.string)
                if len(released):
                    self.info[self.RELEASED_TAG] = released

    @BasicScrapper.store_exceptions
    def get_duration(self) -> None:
        data = self.get_data_component_props('ud-component--course-landing-page-udlite--curriculum')
        if data:
            duration = data['estimated_content_length_in_seconds']
            self.info[self.DURATION_TAG] = self.secs_to_duration(duration)

    @BasicScrapper.store_exceptions
    def download_cover(self) -> None:
        url = self.soup.head.find('meta', property='og:image')
        if url:
            url = url['content']
            self.download_image(url, self.COVER_FILE)

    @BasicScrapper.store_exceptions
    def get_description(self) -> None:
        self.download_cover()

        text = f'![{self.COVER_HINT}]({self.COVER_FILE})\n'

        headline = self.soup.find('div', attrs={'data-purpose': 'lead-headline'})
        if headline:
            text += '\n'
            text += self.italic(headline.string.strip()) + '\n'

        section = self.get_data_component_props('ud-component--course-landing-page-udlite--whatwillyoulearn')
        if section:
            text += '\n'
            text += self.h(1, "What you'll learn")
            text += ''.join(f'* {item.strip()}\n' for item in section['objectives'])

        section = self.get_data_component_props('ud-component--course-landing-page-udlite--requirements')
        if section:
            text += '\n'
            text += self.h(1, 'Requirements')
            text += ''.join(f'* {item.strip()}\n' for item in section['prerequisites'])

        section = self.get_data_component_props('ud-component--course-landing-page-udlite--description')
        if section:
            text += '\n'
            text += self.h(1, 'Description')
            description = self.md.convert(section['description'])
            # description = description.strip('\n')
            text += description

        section = self.get_data_purpose('div', 'target-audience')
        if section:
            text += '\n'
            text += self.h(1, 'Who this course is for')
            audience = self.md.convert(section.ul.decode_contents())
            text += audience

        self.info[self.DESCRIPTION_TAG] = block(text)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
