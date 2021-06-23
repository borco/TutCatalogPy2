import logging
from abc import ABC, abstractmethod
from typing import Any, Final, List, Optional

from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.functions import func

from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


AUTHORS_LABEL: Final[str] = 'authors'
LEARNING_PATHS_LABEL: Final[str] = 'learning paths'
PUBLISHERS_LABEL: Final[str] = 'publishers'
CUSTOM_TAGS_LABEL: Final[str] = 'tags (custom)'
PUBLISHER_TAGS_LABEL: Final[str] = 'tags (publishes)'


class TagsItem:
    _label: str = ''

    def __init__(self, label: Optional[str] = None) -> None:
        self._parent: Optional['TagsItem'] = None
        if label is not None:
            self._label = label
        self._children: List[TagsItem] = []

    @property
    def rows(self) -> int:
        return len(self._children)

    @property
    def row(self) -> int:
        if self._parent is not None:
            return self._parent._children.index(self)
        return 0

    @property
    def parent(self) -> Optional['TagsItem']:
        return self._parent

    @property
    def label(self) -> str:
        return self._label

    def child(self, row: int) -> Optional['TagsItem']:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def append(self, item: 'TagsItem') -> None:
        assert item._parent is None
        item._parent = self
        self._children.append(item)


class TagsGroupItem(TagsItem, ABC):
    def refresh(self) -> None:
        self._children.clear()

        for name, count in self._query():
            self.append(TagsItem(f'{name} ({count})'))

    @abstractmethod
    def _query(self) -> Query:
        pass

    @property
    def label(self) -> str:
        return f'{self._label} ({self.rows})'


class PublishersItem(TagsGroupItem):
    def _query(self) -> Query:
        return (
            dal
            .session
            .query(Publisher.name, func.count(Tutorial.title))
            .outerjoin(Tutorial)
            .group_by(Publisher.id_)
            .order_by(Publisher.name.asc())
        )

    _label = PUBLISHERS_LABEL


class TagsModel(QAbstractItemModel):

    def __init__(self):
        super().__init__()
        self.__root_item = TagsItem('root')
        self.__publishers_item = PublishersItem()
        self.__root_item.append(self.__publishers_item)

    def refresh(self) -> None:
        self.beginResetModel()
        self.__publishers_item.refresh()
        self.endResetModel()

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
