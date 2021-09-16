class Scrapper:
    def scrap(self, location: str, url: str, driver: object, images: bool, verbose: bool) -> bool:
        if 'udemy' not in location.split('.'):
            return False
        if verbose:
            print('Using udemy scrapper')
        return True

    def info(self):
        ret = ''
        return ret
