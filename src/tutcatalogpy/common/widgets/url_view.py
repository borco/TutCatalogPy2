from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices

from tutcatalogpy.common.widgets.elided_label import ElidedLabel


class UrlView(ElidedLabel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setInteractive(True)
        self.triggered.connect(self.__on_triggered)

    def __on_triggered(self, text: str) -> None:
        QDesktopServices.openUrl(QUrl(text, QUrl.StrictMode))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
