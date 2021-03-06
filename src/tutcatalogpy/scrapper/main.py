import os
import sys
import time
import urllib.parse
from typing import Optional

import click
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

import tutcatalogpy.scrapper.domestika as domestika
import tutcatalogpy.scrapper.gumroad as gumroad
import tutcatalogpy.scrapper.newmastersacademy as newmastersacademy
import tutcatalogpy.scrapper.udemy as udemy
from tutcatalogpy.common.files import relative_path


def make_driver(driver_name: str, headless: bool) -> Optional[WebDriver]:
    if driver_name == 'gecko':
        executable_path = relative_path(__file__, 'drivers/geckodriver')
        profile_path = relative_path(__file__, 'profiles/gecko.Default')
        options = webdriver.FirefoxOptions()
        options.headless = headless
        options.add_argument('-profile')
        options.add_argument(profile_path)
        driver = webdriver.Firefox(
            executable_path=executable_path,
            options=options,
            # hard-code the Marionette port so geckodriver can connect
            service_args=['--marionette-port', '2828'],
            service_log_path=os.devnull,
        )
    elif driver_name == 'chrome':
        executable_path = relative_path(__file__, 'drivers/chromedriver')
        profile_path = relative_path(__file__, 'profiles/chrome.Default')
        options = webdriver.ChromeOptions()
        if headless:
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
@click.option('-h/-H', '--headless/--no-headless', default=True, help='Run headless.')
@click.option('-j/-J', '--json/--no-json', 'as_json', default=True, help='Return info as JSON.')
@click.option('--images/--no-images', ' /-I', default=True, help='Download images.')
@click.option('-t', '--timeout', default=0, help='Timeout after finishing scrapping (in seconds).')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output.')
def run(url, driver_name, source_file, images, headless, as_json, timeout, verbose):
    if verbose:
        print(f"""Scrapping:       {url}
    driver:      {driver_name}
    headless:    {headless}
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
        driver = make_driver(driver_name, headless)
        if driver is None:
            print(f'Could not create driver: {driver_name}')
            sys.exit(1)

        driver.get(url)
        source = driver.page_source

        if len(source) == 0:
            if not headless and timeout:
                time.sleep(timeout)
            driver.quit()
            print(f'Nothing to scrap from {url}')
            sys.exit(1)

    scrapped = False
    scrappers = [
        domestika.Scrapper,
        gumroad.Scrapper,
        newmastersacademy.Scrapper,
        udemy.Scrapper,
    ]

    for scrapper_class in scrappers:
        scrapper = scrapper_class(parsed_url.netloc, url, source, images, verbose)
        if scrapper.can_scrap:
            scrapper.scrap()
            print(scrapper.dump(as_json).rstrip('\n'))
            scrapped = True
            break

    if not scrapped:
        print(f"Don't know how to scrap: {url}")
        sys.exit(1)

    if driver:
        if not headless and timeout:
            time.sleep(timeout)
        driver.quit()


if __name__ == '__main__':
    run()
