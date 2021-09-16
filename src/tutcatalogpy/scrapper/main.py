import sys
import time
import urllib.parse
from typing import Optional

import click
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

import tutcatalogpy.scrapper.udemy as udemy
from tutcatalogpy.common.files import relative_path


def make_driver(driver_name: str) -> Optional[WebDriver]:
    if driver_name == 'gecko':
        executable_path = relative_path(__file__, 'drivers/geckodriver')
        profile_path = relative_path(__file__, 'profiles/gecko.Default')
        options = webdriver.FirefoxOptions()
        options.add_argument('-profile')
        options.add_argument(profile_path)
        driver = webdriver.Firefox(
            executable_path=executable_path,
            options=options,
            # hard-code the Marionette port so geckodriver can connect
            service_args=['--marionette-port', '2828'],
        )
    elif driver_name == 'chrome':
        executable_path = relative_path(__file__, 'drivers/chromedriver')
        profile_path = relative_path(__file__, 'profiles/chrome.Default')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument(f'user-data-dir={profile_path}')  # Path to your chrome profile
        driver = webdriver.Chrome(
            executable_path=executable_path,
            options=options,
        )
    else:
        driver = None
    return driver


@click.command()
@click.argument('url')
@click.option('-c', '--chrome', 'driver_name', flag_value='chrome', help='Use chrome and chromedriver.')
@click.option('-g', '--gecko', 'driver_name', flag_value='gecko', default=True, help='Use firefox and geckodriver.')
@click.option('-s', '--source', 'source_file', type=click.File('rb'), help='Use FILENAME instead of downloading from internet.')
@click.option('--images/--no-images', ' /-I', default=True, help='Download images.')
@click.option('-t', '--timeout', default=0, help='Timeout after finishing scrapping (in seconds).')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output.')
def run(url, driver_name, source_file, images, timeout, verbose):
    if verbose:
        print(f"""Scrapping:       {url}
    driver:      {driver_name}
    source:      {source_file}
    images:      {images}
    timeout:     {timeout}
    verbose:     {verbose}
""")
    parsed_url = urllib.parse.urlparse(url)

    driver = None

    if source_file is not None:
        source = source_file.read()

        if len(source) == 0:
            print(f'Nothing to scrap from {source_file.name}')
            sys.exit(1)

    else:
        driver = make_driver(driver_name)
        if driver is None:
            print(f'Could not create driver: {driver_name}')
            sys.exit(1)

        driver.get(url)
        source = driver.page_source

        if len(source):
            time.sleep(timeout)
            driver.quit()
            print(f'Nothing to scrap from {url}')
            sys.exit(1)

    scrapped = False
    scrappers = [
        udemy.Scrapper
    ]

    for scrapper_class in scrappers:
        scrapper = scrapper_class(parsed_url.netloc, url, source, images, verbose)
        if scrapper.can_scrap:
            scrapper.scrap()
            print(scrapper.dump().rstrip('\n'))
            scrapped = True
            break

    if not scrapped:
        print(f"Don't know how to scrap: {url}")
        sys.exit(1)

    if driver:
        time.sleep(timeout)
        driver.quit()


if __name__ == '__main__':
    run()
