from tutcatalogpy.scrapper.basic import Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('gumroad', 'Gumroad', location, url, source, images, verbose)
