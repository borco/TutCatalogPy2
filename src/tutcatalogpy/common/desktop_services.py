from pathlib import Path

from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices


def open_url(path: Path, in_parent: bool = False) -> None:
    if path.exists():
        if in_parent:
            p = path.parent
        else:
            p = path
        QDesktopServices.openUrl(QUrl(f'file://{p}', QUrl.TolerantMode))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
