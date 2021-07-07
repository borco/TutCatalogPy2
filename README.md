# TutCatalogPy2 (WIP)

## About

A catalog for your tutorials. Keeps a cache of the tutorials for fast access and search. Developed in Python and Qt/PySide2.

This incarnation of the TutCatalog is the fourth one, after 2 in C++ and another one in Python.

Main project repo: https://gitlab.com/iborco-software/tutcatalog/tutcatalogpy2

## Project Status

* the main catalog application
  * parse and display info from _info.tc_ files
  * [TODO] edit the _info.tc_ files
* [TODO] the viewer application

![main page](docs/main.png)

## Install

You need to install first [poetry](https://python-poetry.org/) in order to handle any additional dependencies.

Once you have _poetry_ installed, clone the sources and run the commands bellow inside your source directory.

```bash
# go to your source folder
cd .../tutcatalogpy2

# setup virtual environment and install dependencies
poetry install

# start a shell in the virtual environment
poetry shell

# start the catalog
tutcatalogpy

# start the viewer
tutviewerpy

# (optional) create py2app stubs
python setup-catalog.py py2app -A
python setup-viewer.py py2app -A
```

## Misc

* [development notes](docs/development_notes.md)
