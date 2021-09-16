import sys
import sys
import time
import urllib.parse

import click
from selenium import webdriver

import tutcatalogpy.scrapper.udemy as udemy
from tutcatalogpy.common.files import relative_path


def make_driver(driver_name, show_driver):
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
        # options.add_argument('--no-headless')
        options.add_argument(f'user-data-dir={profile_path}')  # Path to your chrome profile
        driver = webdriver.Chrome(
            executable_path=executable_path,
            options=options,
        )
        driver.maximize_window()
    else:
        driver = None
    return driver


@click.command()
@click.argument('url')
@click.option('-c', '--chrome', 'driver_name', flag_value='chrome')
@click.option('-g', '--gecko', 'driver_name', flag_value='gecko', default=True)
@click.option('-s', '--show-driver', default=False)
@click.option('--images/--no-images', ' /-I', default=True)
@click.option('-v', '--verbose', is_flag=True, default=False)
def run(url, driver_name, show_driver, images, verbose):
    if verbose:
        print(f"""Scrapping:       {url}
    driver:      {driver_name}
    show driver: {show_driver}
    images:      {images}
    verbose:     {verbose}
""")
    parsed_url = urllib.parse.urlparse(url)

    scrapped = False
    scrappers = [
        udemy.Scrapper
    ]

    driver = make_driver(driver_name, show_driver)
    if driver is None:
        print(f'Could not create driver: {driver_name}')
        sys.exit(1)

    driver.get(url)

    for scrapper_class in scrappers:
        scrapper = scrapper_class()
        if scrapper.scrap(parsed_url.netloc, url, driver, images, verbose):
            print(scrapper.info())
            scrapped = True
            break

    if not scrapped:
        print(f"Don't know how to scrap: {url}")
        sys.exit(1)

    time.sleep(5)


if __name__ == '__main__':
    run()
