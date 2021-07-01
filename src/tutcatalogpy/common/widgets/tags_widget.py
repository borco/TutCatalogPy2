from dataclasses import dataclass, field
from typing import Any, Final, List, Optional

from PySide2.QtCore import QAbstractItemModel, QAbstractListModel, QEvent, QModelIndex, QObject, QRect, QSize, Qt, Signal
from PySide2.QtGui import QFontMetrics, QPainter, QResizeEvent
from PySide2.QtWidgets import QFrame, QItemDelegate, QListView, QStyleOptionViewItem
from sqlalchemy.sql.schema import Table

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.publisher import Publisher


@dataclass
class TagItem:
    text: str
    index: Optional[int] = field(default=None)
    table: Optional[Table] = field(default=None, init=False)

    def same_index(self, other: 'TagItem') -> bool:
        return other is not None and self.table == other.table and self.index == other.index

    @property
    def selectable(self) -> bool:
        return self.table is not None and self.index is not None


@dataclass
class TextItem(TagItem):
    pass


@dataclass
class AuthorItem(TagItem):
    table = Author


@dataclass
class PublisherItem(TagItem):
    table = Publisher


class TagsModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        self.__items: List[TagItem] = []

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__items)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        if row < 0 or row >= len(self.__items):
            return None

        if role == Qt.DisplayRole:
            return self.__items[row].text
        elif role == Qt.UserRole:
            return self.__items[row]

    def clear(self) -> None:
        self.beginResetModel()
        self.__items.clear()
        self.endResetModel()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = Qt.ItemFlag.ItemIsEnabled
        row = index.row()
        if 0 <= row < len(self.__items):
            item = self.__items[row]
            if item.selectable:
                flags |= Qt.ItemIsSelectable
        return flags

    def add_tag(self, item: TagItem) -> None:
        index = self.index_of(item)
        if index is not None:
            tag = self.__items[index]
            tag.text = item.text
            row = index
            model_index = self.createIndex(row, 0, None)
            self.dataChanged.emit(model_index, model_index)
        else:
            row = len(self.__items)
            self.beginInsertRows(QModelIndex(), row, row)
            self.__items.append(item)
            self.endInsertRows()

    def index_of(self, item: TagItem) -> Optional[int]:
        if item.table is None or item.index is None:
            return None
        else:
            return next((index for index, tag in enumerate(self.__items) if item.same_index(tag)), None)

    def item_at(self, row: int) -> Optional[TagItem]:
        if 0 <= row < len(self.__items):
            return self.__items[row]
        else:
            return None


class TagItemDelegate(QItemDelegate):
    clicked = Signal(Table, int)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        tag: TagItem = index.data(Qt.UserRole)
        if isinstance(tag, TagItem):
            if not tag.selectable:
                font = option.font
                font.setBold(True)
                metrics = QFontMetrics(font)
                return metrics.boundingRect(tag.text).adjusted(0, 0, 5, 0).size()
            else:
                metrics = option.fontMetrics
                rect: QRect = metrics.boundingRect(tag.text)
                return rect.adjusted(0, 0, 5, 0).size()
        return super().sizeHint(option, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        tag: TagItem = index.data(Qt.UserRole)
        if isinstance(tag, TagItem):
            painter.save()
            rect: QRect = option.rect
            font = painter.font()
            if not tag.selectable:
                font.setBold(True)
            else:
                font.setUnderline(True)
            painter.setFont(font)
            painter.drawText(rect, tag.text)
            painter.restore()
        else:
            return super().paint(painter, option, index)

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        tag: TagItem = index.data(Qt.UserRole)
        if isinstance(tag, TagItem):
            if event.type() == QEvent.MouseButtonRelease and tag.selectable:
                self.clicked.emit(tag.table, tag.index)
        return super().editorEvent(event, model, option, index)


class TagsWidget(QListView):
    MINIMUM_HEIGHT: Final[int] = 16
    HORIZONTAL_SPACING: Final[int] = 0
    VERTICAL_SPACING: Final[int] = 0
    VERTICAL_SCROLLBAR_WIDTH: Final[int] = 0

    tag_clicked = Signal(Table, int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__model = TagsModel()
        self.setModel(self.__model)

        self.__delegate = TagItemDelegate()
        self.setItemDelegate(self.__delegate)
        self.__delegate.clicked.connect(self.tag_clicked.emit)

        self.setViewMode(self.IconMode)
        self.setFlow(self.LeftToRight)
        self.setResizeMode(self.Adjust)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet('background-color: transparent;')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def sizeHint(self) -> QSize:
        rect = self.rect()
        width = rect.width()
        height = self.__height_for_width(width)
        return QSize(0, height)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        width = self.rect().width()
        height = self.__height_for_width(width)
        self.setFixedHeight(height)

    def clear(self) -> None:
        self.__model.clear()

    def add_text(self, text: str) -> None:
        self.__model.add_tag(TextItem(text))

    def add_author(self, text: str, index: int) -> None:
        self.__model.add_tag(AuthorItem(text, index))

    def add_publisher(self, text: str, index: int) -> None:
        self.__model.add_tag(PublisherItem(text, index))

    def __horizontal_spacing(self) -> int:
        return self.HORIZONTAL_SPACING

    def __vertical_spacing(self) -> int:
        return self.VERTICAL_SPACING

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.adjustSize()

    def adjustSize(self) -> None:
        width = self.frameRect().width()
        height = self.__height_for_width(width)
        self.setFixedHeight(height)

    def __height_for_width(self, width: int) -> int:
        left: int
        top: int
        right: int
        bottom: int
        left, top, right, bottom = self.getContentsMargins()
        effective_right: int = width - right - self.VERTICAL_SCROLLBAR_WIDTH
        effective_x: int = left
        effective_y: int = top
        x: int = effective_x
        y: int = effective_y
        line_height: int = 0

        for row in range(self.__model.rowCount(QModelIndex())):
            index = self.__model.index(row, 0, QModelIndex())
            item_size_hint = self.__delegate.sizeHint(QStyleOptionViewItem(), index)

            space_x: int = self.__horizontal_spacing()
            space_y: int = self.__vertical_spacing()

            next_x: int = x + item_size_hint.width() + space_x
            if next_x - space_x > effective_right and line_height > 0:
                x = effective_x
                y += line_height + space_y
                next_x = x + item_size_hint.width() + space_x
                line_height = 0

            x = next_x
            line_height = max(line_height, item_size_hint.height())
        return max(self.MINIMUM_HEIGHT, y + line_height + bottom)


# if __name__ == '__main__':
#     from PySide2.QtWidgets import QApplication, QVBoxLayout, QPushButton

#     app = QApplication([])
#     window = QWidget(None)

#     layout = QVBoxLayout()
#     window.setLayout(layout)

#     tags = TagsWidget()
#     layout.addWidget(tags)

#     tags.tag_clicked.connect(lambda table, tag: print(table, tag))
#     tags.add_text('xxx:')
#     tags.add_author('xxx 1', index=1)
#     tags.add_author('xxx 2', index=2)
#     tags.add_text('yyy:')
#     tags.add_publisher('yyy 1', index=1)
#     tags.add_publisher('yyy 2', index=2)

#     btn = QPushButton('test')
#     layout.addWidget(btn)

#     layout.addStretch(1)

#     window.show()

#     app.exec_()

if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
