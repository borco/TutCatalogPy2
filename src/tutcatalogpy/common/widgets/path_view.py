from pathlib import Path
from typing import Optional

from PySide2.QtCore import Qt, QUrl
from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QLabel


class PathView(QLabel):
    __path: Path = Path()
    __text: Optional[str] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.linkActivated.connect(self.__on_link_activated)

    def set_path(self, path: Path, text: Optional[str] = None) -> None:
        self.__path = path
        self.__text = text if text is not None else str(path)
        self.setText(f'<a href="{self.__path}">{self.__text}</a>')

    def __on_link_activated(self, text: str) -> None:
        if self.__path.exists():
            QDesktopServices.openUrl(QUrl(f'file://{self.__path}', QUrl.TolerantMode))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
