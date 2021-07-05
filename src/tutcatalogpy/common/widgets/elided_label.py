from enum import IntEnum, auto
from typing import Optional

from PySide2.QtCore import QPoint, Qt, Signal
from PySide2.QtGui import QCursor, QPaintEvent, QPainter, QPalette
from PySide2.QtWidgets import QAbstractButton, QWidget


class ElidedLabel(QAbstractButton):
    class Tip(IntEnum):
        NO_TIP = 0
        SHOW_DATA = auto()
        SHOW_TEXT = auto()
        SHOW_TEXT_IF_ELIDED = auto()

    textChanged = Signal(str)
    triggered = Signal(str)
    interactivityChanged = Signal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__data: Optional[str] = None
        self.__text: str = ''
        self.__elided: bool = False

        # make sure we trigger the first paint event that determines the minimum height
        self.setMinimumSize(10, 10)

        self.__interactive = False
        self.setInteractive(False)

        self.tip = ElidedLabel.Tip.NO_TIP

    @property
    def elided(self) -> bool:
        return self.__elided

    def interactive(self) -> bool:
        return self.__interactive

    def setInteractive(self, value: bool) -> None:
        if value == self.__interactive:
            return

        self.__interactive = value
        if self.__interactive:
            self.setCursor(Qt.PointingHandCursor)
            self.clicked.connect(lambda: self.triggered.emit(self.__data if self.__data is not None else self.__text))
        else:
            self.setCursor(Qt.ArrowCursor)
            self.clicked.disconnect()
        self.update()
        self.interactivityChanged.emit(self.__interactive)

    def text(self) -> str:
        return self.__text

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)

        if self.isEnabled():
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(QCursor())

    def set_text(self, value: str) -> None:
        # print(f'set text: {value}')
        if value != self.__text:
            self.__text = value
            self.update()
            self.textChanged.emit(self.__text)

    def set_data(self, value: Optional[str]) -> None:
        self.__data = value
        self.update()

    def clear(self) -> None:
        self.set_text('')
        self.set_data(None)

    def paintEvent(self, event: QPaintEvent) -> None:
        # print('ElidedLabel.paintEvent')
        painter = QPainter(self)

        if self.__interactive:
            pen = painter.pen()
            pen.setColor(QPalette().color(QPalette.Link))
            painter.setPen(pen)

            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)

        metrics = painter.fontMetrics()
        elidedContent = metrics.elidedText(self.__text, Qt.ElideRight, self.width())
        painter.drawText(QPoint(0, metrics.ascent()), elidedContent)

        self.setMinimumSize(
            10,
            metrics.boundingRect('X').height() + metrics.underlinePos()
        )

        painter.end()

        self.__elided = (elidedContent != self.__text)
        self.__update_status_tip()

    def __update_status_tip(self) -> None:
        if self.tip == ElidedLabel.Tip.SHOW_DATA and self.__data is not None:
            self.setStatusTip(self.__data)
        elif self.tip == ElidedLabel.Tip.SHOW_TEXT or (self.tip == ElidedLabel.Tip.SHOW_TEXT_IF_ELIDED and self.__elided):
            self.setStatusTip(self.__text)
        else:
            self.setStatusTip('')


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QCheckBox, QLabel, QVBoxLayout

    app = QApplication([])
    window = QWidget(None)

    label = ElidedLabel(window)
    label.set_text('/some/very/very/very/very/long/path')
    label.triggered.connect(lambda url: print(f'clicked: {url}'))

    checkbox = QCheckBox('interactive', window)
    checkbox.toggled.connect(label.setInteractive)
    checkbox.setChecked(True)

    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(QLabel('xxx/xxx/xxx/yyy', window))
    layout.addWidget(checkbox)
    # layout.setContentsMargins(0, 0, 0, 0)

    window.setLayout(layout)

    window.resize(100, 100)
    window.show()

    app.exec_()
