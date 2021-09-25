import doctest
import re

from tutcatalogpy.scrapper.basic import block, Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__(None, 'New Masters Academy', location, url, source, images, verbose)

        self.can_scrap = False
        for loc in ['nma.com', 'nma.art']:
            if location.endswith(loc):
                self.can_scrap = True
                break

    @staticmethod
    def parse_title(value: str) -> str:
        """
        >>> s = Scrapper
        >>> s.parse_title('')
        ''
        >>> s.parse_title('foo - New Masters Academy')
        'foo'
        >>> s.parse_title('foo and bar | New Masters Academy')
        'foo and bar'
        """
        value = re.sub(r'\s*[-\|]*\s*new masters academy', '', value, flags=re.IGNORECASE)
        return value

    @BasicScrapper.store_exceptions
    def get_title(self) -> None:
        self.info.title = self.parse_title(self.soup.title.string)

    def videometa(self):
        return self.soup.find('div', class_='videometa')

    @BasicScrapper.store_exceptions
    def get_authors(self):
        author = str(self.videometa().find('dd').string)
        self.info.authors = [author]

    @staticmethod
    def parse_released(value: str) -> str:
        """
        >>> s = Scrapper
        >>> s.parse_released('https://www.nma.art/wp-content/uploads/2018/02/SH60_topimage-960x300.jpg')
        '2018/02'
        """
        value = re.sub(r'.*uploads/(\d\d\d\d)/(\d\d)/.*', r'\1/\2', value)
        return value

    def cover_url(self) -> str:
        return self.soup.find('img', 'woo-image thumbnail cboxElement')['src']

    @BasicScrapper.store_exceptions
    def get_released(self):
        self.info.released = self.parse_released(self.cover_url())

    @staticmethod
    def parse_level(value: str) -> str:
        """
        >>> s = Scrapper
        >>> s.parse_level('  Beginner Friendly  ')
        'beginner'
        """
        if 'beginner' in value.lower():
            return 'beginner'
        return ''

    @BasicScrapper.store_exceptions
    def get_level(self) -> None:
        div = self.soup.find('div', 'skill-container')
        if div:
            self.info.level = self.parse_level(' '.join(div.stripped_strings))

    @staticmethod
    def parse_duration(value):
        """
        >>> s = Scrapper
        >>> s.parse_duration('')
        ''
        >>> s.parse_duration('3h 20m 46s')
        '3h 20m'
        """
        value = re.sub(r'(\d+)h (\d+)m (\d+)s', r'\1h \2m', value)
        return value

    @BasicScrapper.store_exceptions
    def get_duration(self):
        videometa = self.videometa().find_all('dd')
        self.info.duration = self.parse_duration(videometa[4].string)

    @BasicScrapper.store_exceptions
    def get_tags(self):
        videometa = self.videometa().find_all('dd')
        tags = ''
        for i in [1, 2, 3, 5]:
            if i < len(videometa):
                tags += ''.join(videometa[i].strings) + ','
        tags = [x.strip().lower() for x in tags.split(',') if x.strip() != '']
        tags.sort()
        self.info.tags = tags

    def download_cover(self):
        self.download_image(self.cover_url(), self.COVER_FILE, referer=self.info.url)

    @BasicScrapper.store_exceptions
    def get_description(self):
        if self.with_images:
            self.download_cover()

        description = '![cover](cover.jpg)\n\n'
        description += self.md.convert(str(self.soup.find('div', 'lessondesc')))
        self.info.description = description


if __name__ == '__main__':
    doctest.testmod()
