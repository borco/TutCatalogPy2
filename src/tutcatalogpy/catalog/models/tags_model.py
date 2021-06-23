import enum
import logging
from typing import Any, List, Optional

from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Categories(bytes, enum.Enum):
    label: str

    def __new__(cls, value: int, label: str) -> Any:
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        return obj

    AUTHORS = (0, 'authors')
    LEARNING_PATHS = (1, 'learning paths')
    PUBLISHERS = (2, 'publishers')
    TAGS_CUSTOM = (3, 'tags (custom)')
    TAGS_PUBLISHER = (4, 'tags (publisher)')


class TagsItem:
    def __init__(self, label: str, parent: Optional['TagsItem'] = None) -> None:
        self.__parent = parent
        self.__label = label
        self.__children: List[TagsItem] = []

    @property
    def rows(self) -> int:
        return len(self.__children)

    @property
    def row(self) -> int:
        if self.__parent is not None:
            return self.__parent.__children.index(self)
        return 0

    @property
    def parent(self) -> Optional['TagsItem']:
        return self.__parent

    @property
    def label(self) -> str:
        return f'{self.__label} ({len(self.__children)})'

    def child(self, row: int) -> Optional['TagsItem']:
        if 0 <= row < len(self.__children):
            return self.__children[row]
        return None

    def append(self, item: 'TagsItem') -> None:
        self.__children.append(item)


class TagsModel(QAbstractItemModel):

    def __init__(self):
        super().__init__()

        self.__root_item = TagsItem('root')
        for category in Categories:
            self.__root_item.append(TagsItem(category.label, self.__root_item))

        cat1 = self.__root_item.child(0)
        cat1.append(TagsItem('foo', cat1))
        cat1.append(TagsItem('bar', cat1))

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if self.hasIndex(row, column, parent) is False:
            return QModelIndex()

        parent_item: Optional[TagsItem] = None
        if not parent.isValid():
            parent_item = self.__root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        child_item: TagsItem = child.internalPointer()
        parent_item: Optional[TagsItem] = child_item.parent

        if parent_item == self.__root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row, 0, parent_item)

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def rowCount(self, parent: QModelIndex) -> int:
        if parent.column() > 0:
            return 0

        parent_item: TagsItem = parent.internalPointer() if parent.isValid() else self.__root_item
        return parent_item.rows

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item: TagsItem = index.internalPointer()

        return item.label

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return super().flags(index)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__root_item.label
        return None


tags_model = TagsModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
