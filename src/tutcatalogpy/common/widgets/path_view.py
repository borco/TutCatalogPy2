from pathlib import Path
from typing import Optional

from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices

from tutcatalogpy.common.widgets.elided_label import ElidedLabel


class PathView(ElidedLabel):
    __path: Path = Path()
    __text: Optional[str] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setInteractive(True)
        self.triggered.connect(self.__on_triggered)

    def set_path(self, path: Path, text: Optional[str] = None) -> None:
        self.__path = path
        self.__text = text if text is not None else str(path)
        self.setText(self.__text)
        self.setData(str(self.__path))
        self.setInteractive(path.exists())
        self.setStatusTip(f'Open in external file browser: {self.__path}')

    def __on_triggered(self, text: str) -> None:
        if self.__path.exists():
            QDesktopServices.openUrl(QUrl(f'file://{self.__path}', QUrl.TolerantMode))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
