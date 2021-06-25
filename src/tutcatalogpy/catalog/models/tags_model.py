import logging
from typing import Any, Dict, Final, List, Optional

from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.functions import func

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.base import Search
from tutcatalogpy.common.db.dal import dal, tutorial_author_table
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


AUTHORS_LABEL: Final[str] = 'authors'
LEARNING_PATHS_LABEL: Final[str] = 'learning paths'
PUBLISHERS_LABEL: Final[str] = 'publishers'
CUSTOM_TAGS_LABEL: Final[str] = 'tags (custom)'
PUBLISHER_TAGS_LABEL: Final[str] = 'tags (publishes)'

NO_NAME_LABEL: Final[str] = '(no name)'
UNKNOWN_AUTHOR_LABEL: Final[str] = '(unknown author)'
UNKNOWN_PUBLISHER_LABEL: Final[str] = '(unknown publisher)'


SEARCH_TO_TEXT: Final[Dict[int, str]] = {
    Search.WITHOUT: '- ',
    Search.IGNORED: '',
    Search.WITH: '+ ',
}


class TagsItem:
    _label: str = ''

    def __init__(self, label: Optional[str] = None, data: Optional[Any] = None) -> None:
        self._parent: Optional['TagsItem'] = None
        if label is not None:
            self._label = label
        self._children: List[TagsItem] = []
        self.data = data

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


class AuthorsItem(TagsItem):
    __label = AUTHORS_LABEL
    __no_name_label = UNKNOWN_AUTHOR_LABEL

    def __query(self) -> Query:
        return (
            dal
            .session
            .query(Author, func.count(Tutorial.id_))
            .join(tutorial_author_table)
            .filter(
                tutorial_author_table.c.tutorial_id == Tutorial.id_,
                tutorial_author_table.c.author_id == Author.id_,
            )
            .outerjoin(Tutorial)
            .group_by(Author.id_)
            .order_by(Author.name.asc())
        )

    def refresh(self) -> None:
        self._children.clear()

        if dal.session is None:
            return

        for author, count in (
            dal
            .session
            .query(
                Author,
                func.count(tutorial_author_table.c.tutorial_id),
                )
            .outerjoin(tutorial_author_table)
            .filter(tutorial_author_table.c.author_id == Author.id_)
            .group_by(Author.id_)
            .order_by(Author.name)
        ):
            name = author.name
            if name is None or len(name) == 0:
                name = self.__no_name_label
            self.append(TagsItem(f'{name} ({count})', author))

    @property
    def label(self) -> str:
        return f'{self.__label} ({self.rows})'


class PublishersItem(TagsItem):
    __label = PUBLISHERS_LABEL
    __no_name_label = UNKNOWN_PUBLISHER_LABEL

    def refresh(self) -> None:
        self._children.clear()

        if dal.session is None:
            return

        for publisher, count in (
            dal
            .session
            .query(Publisher, func.count(Tutorial.id_))
            .outerjoin(Tutorial)
            .group_by(Publisher.id_)
            .order_by(Publisher.name.asc())
        ):
            name = publisher.name
            if name is None or len(name) == 0:
                name = self.__no_name_label
            self.append(TagsItem(f'{name} ({count})', publisher))

    @property
    def label(self) -> str:
        return f'{self.__label} ({self.rows})'


class TagsModel(QAbstractItemModel):

    TOP_TABLES: Final = (Author, Publisher)

    search_changed = Signal()

    def __init__(self):
        super().__init__()
        self.__root_item = TagsItem('root')

        self.__authors_item = AuthorsItem()
        self.__root_item.append(self.__authors_item)

        self.__publishers_item = PublishersItem()
        self.__root_item.append(self.__publishers_item)

        self.__top_items = [
            self.__authors_item,
            self.__publishers_item,
        ]

    def refresh(self) -> None:
        self.beginResetModel()
        for item in self.__top_items:
            item.refresh()
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
        if item.data is not None:
            return SEARCH_TO_TEXT[item.data.search] + item.label
        else:
            return item.label

    def cycle_search_flag(self, index: QModelIndex) -> None:
        if not index.isValid():
            return

        item: TagsItem = index.internalPointer()
        if item.data is None:
            return

        next_search = {
            Search.IGNORED: Search.WITH,
            Search.WITH: Search.WITHOUT,
            Search.WITHOUT: Search.IGNORED,
        }
        item.data.search = next_search[item.data.search]
        dal.session.commit()
        self.dataChanged.emit(index, index)
        self.search_changed.emit()

    def clear_search_flags(self) -> None:
        if dal.session is None:
            return

        for table in self.TOP_TABLES:
            dal.session.query(table).update({table.search: Search.IGNORED})
        dal.session.commit()

        self.refresh()
        self.search_changed.emit()


tags_model = TagsModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
