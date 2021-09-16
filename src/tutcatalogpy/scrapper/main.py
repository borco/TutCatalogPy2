import click


@click.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--images/--no-images', ' /-I', default=True)
@click.option('-c', '--chrome', 'driver', flag_value='chrome')
@click.option('-g', '--gecko', 'driver', flag_value='gecko', default=True)
@click.argument('url')
def run(url, images, driver, verbose):
    if verbose:
        print(f"""Scrapping:    {url}
    driver:   {driver}
    images:   {images}
    verbose:  {verbose}
""")


if __name__ == '__main__':
    run()
