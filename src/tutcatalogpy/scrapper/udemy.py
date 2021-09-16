from tutcatalogpy.scrapper.basic import Scrapper as BasicScrapper


class Scrapper(BasicScrapper):
    def __init__(self, location: str, url: str, source: str, images: bool, verbose: bool) -> None:
        super().__init__('udemy', 'Udemy', location, url, source, images, verbose)

    def get_title(self) -> None:
        title = self.soup.find('h1', attrs={'data-purpose': 'lead-title'})
        if title and title.string:
            self.info[self.TITLE_TAG] = title.string.replace(':', ' -').strip()

    def get_authors(self) -> None:
        authors = []
        a_tags = self.soup.find('div', attrs={'data-purpose': 'instructor-name-top'}).find_all('a')
        for a_tag in a_tags:
            name = a_tag.span.string.strip()
            if name:
                authors.append(name)
        if len(authors):
            self.info[self.AUTHORS_TAG] = authors
