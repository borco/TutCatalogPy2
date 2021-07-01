# A flowing layout
# https://doc.qt.io/qt-5/qtwidgets-layouts-flowlayout-example.html
# https://gist.github.com/Cysu/7461066

from typing import List, Optional

from PySide2.QtCore import QPoint, QRect, QSize, Qt
from PySide2.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QStyle, QWidget


class FlowLayout(QLayout):
    def __init__(self, margin: int = -1, horizontal_spacing: int = -1, vertical_spacing: int = -1) -> None:
        super().__init__(None)

        self.setContentsMargins(margin, margin, margin, margin)
        self.__h_space: int = horizontal_spacing
        self.__v_space: int = vertical_spacing
        self.__items: List[QLayoutItem] = []

    def __del__(self) -> None:
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QLayoutItem) -> None:
        self.__items.append(item)

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self.__do_layout(QRect(0, 0, width, 0), True)

    def count(self) -> int:
        return len(self.__items)

    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self.__items):
            return self.__items[index]
        else:
            return None

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.__items:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

        return size

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.__do_layout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self.__items):
            return self.__items.pop(index)
        else:
            return None

    def __horizontal_spacing(self) -> int:
        if self.__h_space >= 0:
            return self.__h_space
        else:
            return self.__smart_spacing(QStyle.PM_LayoutHorizontalSpacing)

    def __vertical_spacing(self) -> int:
        if self.__v_space >= 0:
            return self.__v_space
        else:
            return self.__smart_spacing(QStyle.PM_LayoutVerticalSpacing)

    def __do_layout(self, rect: QRect, test_only: bool) -> int:
        left: int
        top: int
        right: int
        bottom: int
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x: int = effective_rect.x()
        y: int = effective_rect.y()
        line_height: int = 0

        for item in self.__items:
            wid = item.widget()

            space_x: int = self.__horizontal_spacing()
            if space_x == -1:
                space_x = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)

            space_y: int = self.__vertical_spacing()
            if space_y == -1:
                space_y = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            next_x: int = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y += line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.bottom() + bottom

    def __smart_spacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            pw: QWidget = parent
            return pw.style().pixelMetric(pm, None, pw)
        else:
            pl: QLayout = parent
            return pl.spacing()


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QLabel, QPushButton

    app = QApplication([])
    window = QWidget(None)

    layout = FlowLayout()
    window.setLayout(layout)

    layout.addWidget(QLabel('authors:'))
    for i in range(10):
        layout.addWidget(QLabel(f'Author {i}'))

    layout.addWidget(QLabel('publishers:'))
    for i in range(10):
        layout.addWidget(QLabel(f'Publisher {i}'))

    window.resize(100, 100)
    window.show()

    app.exec_()
