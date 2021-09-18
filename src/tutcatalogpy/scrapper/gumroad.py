import doctest
import re

from tutcatalogpy.scrapper.basic import block, Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('gumroad', 'Gumroad', location, url, source, images, verbose)

    @BasicScrapper.store_exceptions
    def get_title(self):
        self.info[self.TITLE_TAG] = self.soup.head.find('meta', attrs={'property':'og:title'})['content']

    @BasicScrapper.store_exceptions
    def get_authors(self):
        author = str(self.soup.select_one('h3.author-byline > a').string)
        self.info[self.AUTHORS_TAG] = [author]

    @BasicScrapper.store_exceptions
    def get_description(self) -> None:
        if self.with_images:
            self.download_cover()

        description = self.soup.select_one('blockquote.product-description').decode_contents()
        description = self.COVER_LINE + self.md.convert(description)
        self.info[self.DESCRIPTION_TAG] = block(description)

    def download_cover(self) -> None:
        url = self.soup.head.find('meta', property='og:image')
        if url:
            url = url['content']
            self.download_image(url, self.COVER_FILE)


if __name__ == '__main__':
    doctest.testmod()
