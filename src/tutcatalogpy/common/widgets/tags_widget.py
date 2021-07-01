from dataclasses import dataclass, field
from typing import Any, List, Optional

from PySide2.QtCore import QAbstractItemModel, QAbstractListModel, QModelIndex, QObject, Qt, Signal
from PySide2.QtWidgets import QFrame, QListView, QStyledItemDelegate, QWidget
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
        return next((index for index, tag in enumerate(self.__items) if item.same_index(tag)), None)


class TagItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)


class TagsWidget(QListView):
    tag_clicked = Signal(Table, int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__model = TagsModel()
        super().setModel(self.__model)

        self.__delegate = TagItemDelegate()
        self.setItemDelegate(self.__delegate)

        self.setViewMode(self.IconMode)
        self.setFlow(self.LeftToRight)
        self.setResizeMode(self.Adjust)
        self.setFrameStyle(QFrame.NoFrame)

    def setModel(self, model: QAbstractItemModel) -> None:
        raise RuntimeError('setting model for TagsWidget is not supported')

    def clear(self) -> None:
        self.__model.clear()

    def add_text(self, text: str) -> None:
        self.__model.add_tag(TextItem(text))

    def add_author(self, text: str, index: int) -> None:
        self.__model.add_tag(AuthorItem(text, index))

    def add_publisher(self, text: str, index: int) -> None:
        self.__model.add_tag(PublisherItem(text, index))


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QVBoxLayout

    app = QApplication([])
    window = QWidget(None)

    layout = QVBoxLayout()
    window.setLayout(layout)

    tags = TagsWidget()
    layout.addWidget(tags)

    tags.tag_clicked.connect(lambda table, tag: print(table, tag))
    tags.add_text('xxx:')
    tags.add_author('xxx 1', index=1)
    tags.add_author('xxx 2', index=2)
    tags.add_text('yyy:')
    tags.add_publisher('yyy 1', index=1)
    tags.add_publisher('yyy 2', index=2)

    window.resize(100, 100)
    window.show()

    app.exec_()
