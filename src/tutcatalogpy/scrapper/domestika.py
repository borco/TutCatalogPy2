import re
from typing import Dict, List

from tutcatalogpy.scrapper.basic import block, Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('domestika', 'Domestika', location, url, source, images, verbose)

    @BasicScrapper.store_exceptions
    def get_title(self) -> None:
        title = (
            self.soup
            .find('div', class_='course-header-new')
            .find('h1', class_='course-header-new__title')
            .find('a').string
        )
        self.info[self.TITLE_TAG] = self.valid_fs_name(title)

    @BasicScrapper.store_exceptions
    def get_authors(self) -> None:
        authors = []
        for a in (self.soup
                .find('div', class_='course-header-new')
                .find_all('a', class_='js-teacher-popover-link')):
            authors.append(str(a.string))

        self.info[self.AUTHORS_TAG] = authors

    @staticmethod
    def parse_duration(value):
        """
        >>> t = Scrapper
        >>> t.parse_duration('\\n\\n16 Lessons (2h 33m)\\n')
        '2h 33m'
        """
        p = re.compile(r'.*\((.*)\)')
        match = p.match(value.replace('\n', ' '))
        return match.group(1)

    @BasicScrapper.store_exceptions
    def get_duration(self):
        tag = (self.soup
            .find(id='js-sidebar-course')
            .find('ul', class_="course-details-list")
            .find('i', class_='a-icon-film')
            .parent)
        self.info[self.DURATION_TAG] = self.parse_duration(tag.text)

    @staticmethod
    def parse_level(value):
        """
        >>> t = Scrapper
        >>> t.parse_level('\\n\\nLevel:\\nBeginner\\n')
        'beginner'
        """
        value = value.replace('\n', ' ')
        p = re.compile(r'\s*Level:\s*(\S*)\s*')
        match = p.match(value)
        return match.group(1).lower()

    @BasicScrapper.store_exceptions
    def get_level(self):
        tag = (self.soup.find(id='js-sidebar-course')
            .find('ul', class_="course-details-list")
            .find('i', class_='a-icon-chart-bar')
            .parent)

        self.info[self.LEVEL_TAG] = self.parse_level(tag.text)

    @BasicScrapper.store_exceptions
    def get_description(self):
        # process text
        content = self.soup.find(id='main-content')

        description = ''

        short_description = content.find('h2', class_='course-header-new__short-description')
        description += self.h(1, short_description.string.strip())

        landing_description = content.find('div', class_='course-landing__description')
        for p in landing_description.find('div', class_='text-body-bigger-new').find_all('p'):
            text = p.decode_contents()

            if text.startswith('<div') and text.endswith('</div>'):
                continue

            if len(text):
                description += self.md.convert(text) + '\n\n'

        subtitles = content.find_all('h3', class_='h2 course-landing__description__title')
        for subtitle in subtitles:
            description += self.h(1, subtitle.string.strip())
            div = subtitle.find_next_sibling('div', class_='text-body-bigger-new')
            description += self.md.convert(div.decode_contents()) + '\n\n'

        description += self.h(1, 'Teacher Details')
        description += self.md.convert(str(content.find('div', class_='course-teacher-new__summary')))

        description += self.h(1, 'Contents')
        sections = content.find_all('li', 'toc-new__item')
        for index, section in enumerate(sections):
            prefix = f'U{index + 1}' if (index < len(sections) - 1) else 'FP'
            title = section.find('h4', 'toc-new__unit-title')
            description += f'\n**{prefix} {title.string.strip()}**\n\n'
            for item in section.find_all('div', 'toc-new__lesson-title'):
                description += f'1. {item.string.strip()}\n'

        # process images
        self.download_cover()

        image_urls = self.find_images(description)
        images = self.download_images(image_urls)
        description = self.replace_images(description, images)

        description = f'![{self.COVER_HINT}]({self.COVER_FILE})\n\n' + description

        self.info[self.DESCRIPTION_TAG] = block(description)

    def download_cover(self) -> None:
        if self.with_images:
            content = self.soup.find(id='main-content')
            div = content.find('div', class_='video-container')
            url = div.find('img')['src']
            self.download_image(url, self.COVER_FILE)

    def find_images(self, description: str) -> List[str]:
        return re.findall(r'!\[[^\]]*\]\(([^\)]*)\)', description)

    def download_images(self, image_urls: List[str]) -> Dict[str, str]:
        images = {}
        for index, url in enumerate(image_urls):
            local_file = f'image{index + 1}.jpg'
            images[url] = local_file
            if self.with_images:
                self.download_image(url, local_file)

        return images

    def replace_images(self, description: str, images: Dict[str, str]) -> str:
        for url, local_file in images.items():
            description = description.replace(f'({url})', f'({local_file})')
        description = re.sub(r'\s*!\[', r'\n\n![', description)
        description = re.sub(r'!\[\]\(', '![image](', description)
        return description


if __name__ == '__main__':
    import doctest
    doctest.testmod()
