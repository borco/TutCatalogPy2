import json
import re

from tutcatalogpy.scrapper.basic import Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('udemy', 'Udemy', location, url, source, images, verbose)

    def get_title(self) -> None:
        title = self.soup.find('h1', attrs={'data-purpose': 'lead-title'})
        if title and title.string:
            self.info[self.TITLE_TAG] = self.valid_fs_name(title.string)

    def get_authors(self) -> None:
        authors = []
        a_tags = self.soup.find('div', attrs={'data-purpose': 'instructor-name-top'}).find_all('a')
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

    def get_released(self) -> None:
        div = self.soup.find('div', attrs={'data-purpose': 'last-update-date'})
        if div:
            span = div.find_all('span')[-1]
            if span:
                released = self.parse_released(span.string)
                if len(released):
                    self.info[self.RELEASED_TAG] = released

    def get_duration(self) -> None:
        div = self.soup.find('div', 'ud-component--course-landing-page-udlite--curriculum')
        if div:
            data = json.loads(div['data-component-props'])
            duration = data['estimated_content_length_in_seconds']
            self.info[self.DURATION_TAG] = self.secs_to_duration(duration)
        pass

    def get_level(self) -> None:
        pass

    def get_tags(self) -> None:
        pass

    def get_description(self) -> None:
        pass

    def get_images(self) -> None:
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
