from tutcatalogpy.scrapper.basic import Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('udemy', 'Udemy', location, url, source, images, verbose)

    def get_title(self) -> None:
        title = self.soup.find('h1', attrs={'data-purpose': 'lead-title'})
        if title and title.string:
            self.info['title'] = title.string.strip()
