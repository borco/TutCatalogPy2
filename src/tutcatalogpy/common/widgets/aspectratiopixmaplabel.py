# https://stackoverflow.com/questions/8211982/qt-resizing-a-qlabel-containing-a-qpixmap-while-keeping-its-aspect-ratio
from typing import Optional

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QPixmap, QResizeEvent
from PySide2.QtWidgets import QLabel


class AspectRatioPixmapLabel(QLabel):

    __pixmap: Optional[QPixmap] = None

    def __init__(self, parent=None) -> None:
        super().__init__('', parent=parent)
        self.setMinimumSize(1, 1)
        self.setScaledContents(False)

    def setPixmap(self, pixmap: Optional[QPixmap]) -> None:
        self.__pixmap = pixmap
        super().setPixmap(self.__scaled_pixmap())

    def heightForWidth(self, width: int) -> int:
        return self.height() if self.__pixmap is None else int(self.__pixmap.height() * width / self.__pixmap.width())

    def sizeHint(self) -> QSize:
        if self.__pixmap is None:
            return self.size()

        width = min(self.width(), self.__pixmap.width())
        height = self.heightForWidth(width)
        if height > self.height():
            height = self.height()
            width = int(self.__pixmap.width() * height / self.__pixmap.height())
        return QSize(width, height)

    def __scaled_pixmap(self) -> QPixmap:
        if self.__pixmap is None:
            return QPixmap()
        else:
            return self.__pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.__pixmap is not None:
            super().setPixmap(self.__scaled_pixmap())


if __name__ == '__main__':
    from tutcatalogpy.catalog.widgets.cover_dock import run
    run()
