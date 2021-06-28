import enum
import logging
from dataclasses import dataclass
from typing import Any, Dict, Final, Optional

from humanize import naturalsize
from PySide2.QtCore import QAbstractTableModel, QDateTime, QModelIndex, Qt, Signal
from PySide2.QtGui import QIcon
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column

from tutcatalogpy.catalog.widgets.search_dock import SearchDock
from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.base import FIELD_SEPARATOR, Search
from tutcatalogpy.common.db.dal import dal, tutorial_author_table
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.files import relative_path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

AUTHORS_SEPARATOR: Final[str] = ', '


@dataclass
class QueryResult:
    folder: Optional[Folder] = None
    has_cover: Optional[bool] = None
    authors: Optional[str] = None


class Columns(bytes, enum.Enum):
    label: str  # column label displayed in the table view
    column: Column
    alias: Optional[str]

    def __new__(cls, value: int, label: str, column: Column, alias: Optional[str] = None):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.column = column
        obj.alias = alias
        return obj

    CHECKED = (0, 'Checked', Folder.checked)
    INDEX = (1, 'Index', Folder.id_)
    ONLINE = (2, 'Online', Disk.online)
    LOCATION = (3, 'Location', Disk.location)
    HAS_COVER = (4, 'Cover', (Folder.cover_id != None), 'has_cover')
    DISK_NAME = (5, 'Disk', Disk.disk_name)
    FOLDER_PARENT = (6, 'Folder Parent', Folder.folder_parent)
    FOLDER_NAME = (7, 'Folder Name', Folder.folder_name)
    PUBLISHER = (8, 'Publisher', Publisher.name)
    TITLE = (9, 'Title', Tutorial.title)
    AUTHORS = (10, 'Authors', Tutorial.all_authors)
    SIZE = (11, 'Size', Folder.size)
    CREATED = (12, 'Created', Folder.created)
    MODIFIED = (13, 'Modified', Folder.modified)


class TutorialsModel(QAbstractTableModel):

    NO_COVER_ICON: Final[str] = relative_path(__file__, '../../resources/icons/no_cover.svg')
    OFFLINE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/offline.svg')
    REMOTE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/remote.svg')

    summary_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.__query_results_cache: Dict[int, QueryResult] = {}
        self.__row_count: int = 0
        self.__sort_column: int = 0
        self.__sort_ascending: bool = True
        self.__search_text: str = ''
        self.__only_show_checked_disks: bool = False
        self.__no_cover_icon: Optional[QIcon] = None

    def init_icons(self) -> None:
        self.__no_cover_icon = QIcon(self.NO_COVER_ICON)
        self.__offline_icon = QIcon(self.OFFLINE_ICON)
        self.__remote_icon = QIcon(self.REMOTE_ICON)

    def search(self, search_dock: SearchDock, force: bool = False) -> None:
        if search_dock.text == self.__search_text and search_dock.only_show_checked_disks == self.__only_show_checked_disks and not force:
            return

        self.__search_text: str = search_dock.text
        self.__only_show_checked_disks: bool = search_dock.only_show_checked_disks

        log.info("Search for: '%s' (only show checked disks: %s)", self.__search_text, self.__only_show_checked_disks)
        self.refresh()

    def columnCount(self, index) -> int:
        return len(Columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in [
                Columns.INDEX.value,
                Columns.CHECKED.value,
            ]:
                return ''
            else:
                return Columns(section).label

        return super().headerData(section, orientation, role)

    def rowCount(self, index) -> int:
        return self.__row_count

    def refresh(self) -> None:
        self.beginResetModel()
        self.__update_cached_query()
        self.endResetModel()
        log.debug('Folder model updated row count: %s.', self.__row_count)

    def data(self, index, role) -> Any:
        row = index.row()

        result = self.__cached_query_result(row)

        folder = result.folder

        if folder is None:
            return None

        column = index.column()

        if role == Qt.DecorationRole:
            if column == Columns.HAS_COVER.value:
                return None if result.has_cover else self.__no_cover_icon
            elif column == Columns.ONLINE.value:
                return None if folder.disk.online else self.__offline_icon
            elif column == Columns.LOCATION.value:
                return None if folder.disk.location == Disk.Location.LOCAL else self.__remote_icon
        elif role == Qt.CheckStateRole:
            if column == Columns.CHECKED.value:
                return Qt.Checked if folder.checked else Qt.Unchecked
        elif role == Qt.DisplayRole:
            if column == Columns.INDEX.value:
                return folder.id_
            elif column == Columns.DISK_NAME.value:
                return folder.disk.disk_name
            elif column == Columns.FOLDER_PARENT.value:
                return folder.folder_parent
            elif column == Columns.FOLDER_NAME.value:
                return folder.folder_name
            elif column == Columns.PUBLISHER.value:
                return folder.tutorial.publisher.name
            elif column == Columns.TITLE.value:
                return folder.tutorial.title
            elif column == Columns.SIZE.value:
                value = folder.size
                return naturalsize(value) if value else ''
            elif column == Columns.CREATED.value:
                return QDateTime.fromSecsSinceEpoch(folder.created.timestamp())
            elif column == Columns.MODIFIED.value:
                return QDateTime.fromSecsSinceEpoch(folder.modified.timestamp())
            elif column == Columns.AUTHORS.value:
                return folder.tutorial.all_authors[1:-1].replace(FIELD_SEPARATOR, ', ')

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        row = index.row()

        folder = self.__cached_query_result(row).folder

        if folder is None:
            return False

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == Columns.CHECKED.value:
                folder.checked = (value == Qt.Checked)
                dal.session.commit()
                del self.__query_results_cache[row]
                return True
        return False

    def flags(self, index: QModelIndex) -> Any:
        column = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | super().flags(index)

        if column == Columns.CHECKED.value:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def __base_query(self) -> Query:
        query = (
            dal
            .session
            .query(
                Folder,
                Columns.HAS_COVER.column.label(Columns.HAS_COVER.alias),
            )
        )

        return query

    def __query_result(self, row: int) -> QueryResult:
        query = self.__cached_query
        folder, has_cover = query.offset(row).limit(1).first()
        return QueryResult(folder, has_cover)

    def __joined_query(self, query: Query) -> Query:
        query = (
            query
            .join(Disk)
            .join(Tutorial)
            .join(Publisher)
            .filter(
                Folder.tutorial_id == Tutorial.id_,
                Tutorial.publisher_id == Publisher.id_,
                tutorial_author_table.c.tutorial_id == Tutorial.id_,
                tutorial_author_table.c.author_id == Author.id_
            )
            .group_by(Tutorial.id_)
        )

        return query

    def __filtered_query(self, query: Query) -> Query:
        if self.__only_show_checked_disks:
            query = query.filter(Disk.checked == True)  # noqa: E712

        if len(self.__search_text):
            for key in self.__search_text.split():
                query = (
                    query
                    .filter((Disk.disk_parent + '/' + Disk.disk_name + '/' + Folder.folder_parent + '/' + Folder.folder_name)
                    .like(f'%{key}%'))
                )

        for publisher in dal.session.query(Publisher).filter(Publisher.search == Search.INCLUDE):
            query = query.filter(Publisher.id_ == publisher.id_)

        for publisher in dal.session.query(Publisher).filter(Publisher.search == Search.EXCLUDE):
            query = query.filter(Publisher.id_ != publisher.id_)

        for author in dal.session.query(Author).filter(Author.search == Search.INCLUDE):
            query = query.filter(Tutorial.all_authors.like(f'%{FIELD_SEPARATOR}{author.name}{FIELD_SEPARATOR}%'))

        for author in dal.session.query(Author).filter(Author.search == Search.INCLUDE):
            query = query.filter(Tutorial.all_authors.like(f'%{FIELD_SEPARATOR}{author.name}{FIELD_SEPARATOR}%'))

        for author in dal.session.query(Author).filter(Author.search == Search.EXCLUDE):
            query = query.filter(Tutorial.all_authors.not_like(f'%{FIELD_SEPARATOR}{author.name}{FIELD_SEPARATOR}%'))

        return query

    def __sorted_query(self, query: Query) -> Query:
        column: Column = Columns(self.__sort_column).column

        if column in [
            Columns.TITLE.column,
            Columns.PUBLISHER.column,
        ]:
            query = query.order_by(column.is_(None), column.is_(''))
        query = query.order_by(column.is_(None), column.is_(FIELD_SEPARATOR * 2))
        column = column.asc() if self.__sort_ascending else column.desc()
        query = query.order_by(column)
        if column not in [Folder.folder_name, Folder.id_]:
            query = query.order_by(Folder.folder_name.asc())

        return query

    def __update_cached_query(self) -> None:
        if dal.connected:
            self.__cached_query = self.__sorted_query(self.__filtered_query(self.__joined_query(self.__base_query())))
            self.__row_count = self.__cached_query.count()
            total_size = self.__total_size()
        else:
            self.__cached_query = None
            self.__row_count = 0
            total_size = 0
        self.__query_results_cache.clear()

        total_size = naturalsize(total_size) if total_size > 0 else '0'
        self.summary_changed.emit(f'F: {self.__row_count} ({total_size})')

    def __cached_query_result(self, row: int) -> QueryResult:
        if row < 0 or row >= self.__row_count:
            return QueryResult()

        result = self.__query_results_cache.get(row, QueryResult())

        if result.folder is None:
            result = self.__query_result(row)

            if result.folder is None:
                return QueryResult()

        self.__query_results_cache[row] = result

        return result

    def folder(self, row: int) -> Optional[Folder]:
        return self.__cached_query_result(row).folder

    def sort(self, index: int, sort_oder: Qt.SortOrder) -> None:
        self.beginResetModel()
        self.__sort_column = index
        self.__sort_ascending = (sort_oder == Qt.SortOrder.AscendingOrder)
        self.__update_cached_query()
        self.endResetModel()

    def __total_size(self) -> int:
        visible_folders = self.__filtered_query(
            self.__joined_query(
                (
                    dal
                    .session
                    .query(Folder.id_)
                )
            )
        )

        total_size = (
            dal
            .session
            .query(func.sum(Folder.size))
            .where(Folder.id_.in_(visible_folders))
        ).scalar()

        return total_size if total_size is not None else 0


tutorials_model = TutorialsModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
