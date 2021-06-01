# TutCatalogPy

## Development Environment

```bash
# setup virtual environment and install dependencies
poetry install

# start the catalog
python -m tutcatalogpy.catalog

# start the viewer
python -m tutcatalogpy.viewer

# create py2app stubs
python setup-catalog.py py2app -A
# python setup-viewer.py py2app -A
```

## Notes

### Columns can't be moved

* open the .ini file
* delete the _header_state_ entries

### App crashing on start (MacOS)

**Problem:**

Got this error when setting _system_ python with _pyenv_.

**Solution:**

* set a _custom_ python with pyenv
* logout
* login

```bash
# set custom python version with pyenv
pyenv global 3.9.1
```
