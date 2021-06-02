"""
This is a setup.py script generated by py2applet

Usage:
    python setup-catalog.py py2app
"""

from setuptools import setup

APP = ['src/tutcatalogpy/catalog/main.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': 'src/tutcatalogpy/resources/icons/catalog.icns',
}

setup(
    name='TutCatalogPy2 Catalog',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)