# Development Notes

## Columns can't be moved

* open the .ini file
* delete the _header_state_ entries

## App crashing on start (MacOS)

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

## Determine StartupWMClass

```bash
# run tutcatalogpy
# run xprop
# click with the mouse on the tutcatalogpy2 window
# use one of the strings printed by xprop in the .desktop file
xprop WM_CLASS
WM_CLASS(STRING) = "tutcatalogpy", "tutcatalogpy2-catalog"
```
