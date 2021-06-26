import logging
from enum import Enum
from typing import Any, Dict, Final, Optional

from humanize import naturalsize
from PySide2.QtCore import QAbstractTableModel, QDateTime, QModelIndex, Qt, Signal
from PySide2.QtGui import QIcon
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column

from tutcatalogpy.catalog.widgets.search_dock import SearchDock
from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.base import Search
from tutcatalogpy.common.db.dal import dal, tutorial_author_table
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.files import relative_path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

AUTHORS_SEPARATOR: Final[str] = ', '


class ColumnEnum(bytes, Enum):
    label: str  # column label displayed in the table view

    def __new__(cls, value: int, label: str):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        return obj


class TutorialsModel(QAbstractTableModel):

    class Columns(ColumnEnum):
        CHECKED = (0, 'Checked')
        INDEX = (1, 'Index')
        ONLINE = (2, 'Online')
        HAS_COVER = (3, 'Cover')
        DISK_NAME = (4, 'Disk')
        FOLDER_PARENT = (5, 'Folder Parent')
        FOLDER_NAME = (6, 'Folder Name')
        # PUBLISHER = (7, 'Publisher', 'publisher_name', Publisher.name)
        # TITLE = (8, 'Title', 'tutorial_title', Tutorial.title)
        # AUTHORS = (9, 'Authors', 'authors', func.group_concat(Author.name, AUTHORS_SEPARATOR))
        # SIZE = (10, 'Size', 'size', Folder.size)
        # CREATED = (11, 'Created', 'created', Folder.created)
        # MODIFIED = (12, 'Modified', 'modified', Folder.modified)

    NO_COVER_ICON: Final[str] = relative_path(__file__, '../../resources/icons/no_cover.svg')
    OFFLINE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/offline.svg')

    summary_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.__cache: Dict[int, Any] = {}
        self.__row_count: int = 0
        self.__sort_column: int = 0
        self.__sort_ascending: bool = True
        self.__search_text: str = ''
        self.__only_show_checked_disks: bool = False
        self.__no_cover_icon: Optional[QIcon] = None

    def init_icons(self) -> None:
        self.__no_cover_icon = QIcon(self.NO_COVER_ICON)
        self.__offline_icon = QIcon(self.OFFLINE_ICON)

    def search(self, search_dock: SearchDock, force: bool = False) -> None:
        if search_dock.text == self.__search_text and search_dock.only_show_checked_disks == self.__only_show_checked_disks and not force:
            return

        self.__search_text: str = search_dock.text
        self.__only_show_checked_disks: bool = search_dock.only_show_checked_disks

        log.info("Search for: '%s' (only show checked disks: %s)", self.__search_text, self.__only_show_checked_disks)
        self.refresh()

    def columnCount(self, index) -> int:
        return len(TutorialsModel.Columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in [
                TutorialsModel.Columns.INDEX.value,
                TutorialsModel.Columns.CHECKED.value,
            ]:
                return ''
            else:
                return TutorialsModel.Columns(section).label

        return super().headerData(section, orientation, role)

    def rowCount(self, index) -> int:
        return self.__row_count

    def refresh(self) -> None:
        self.beginResetModel()
        if dal.connected:
            self.__cached_query = self.__filtered_and_sorted(self.__joined(self.__query()))
            self.__row_count = self.__cached_query.count()
        else:
            self.__cached_query = None
            self.__row_count = 0
        self.__cache.clear()
        self.endResetModel()
        log.debug('Folder model updated row count: %s.', self.__row_count)

        total_size = self.total_size()
        total_size = naturalsize(total_size) if total_size > 0 else '0'
        self.summary_changed.emit(f'F: {self.__row_count} ({total_size})')

    def data(self, index, role) -> Any:
        row = index.row()

        folder: Optional[Folder] = self.folder(row)

        if folder is None:
            return None

        column = index.column()

        # value = getattr(tutorial, TutorialsModel.Columns(column).alias)
        # if role == Qt.DecorationRole:
        #     if column == TutorialsModel.Columns.HAS_COVER.value:
        #         return None if value else self.__no_cover_icon
        #     elif column == TutorialsModel.Columns.ONLINE.value:
        #         return None if value else self.__offline_icon
        # if role == Qt.CheckStateRole:
        #     if column == TutorialsModel.Columns.CHECKED.value:
        #         return Qt.Checked if value else Qt.Unchecked
        # elif role == Qt.DisplayRole:
        #     if column == TutorialsModel.Columns.SIZE.value:
        #         return naturalsize(value) if value else ''
        #     elif column in [
        #         TutorialsModel.Columns.HAS_COVER.value,
        #         TutorialsModel.Columns.CHECKED.value,
        #         TutorialsModel.Columns.ONLINE.value,
        #     ]:
        #         return None
        #     elif column in [TutorialsModel.Columns.CREATED.value, TutorialsModel.Columns.MODIFIED.value]:
        #         return QDateTime.fromSecsSinceEpoch(value.timestamp())
        #     else:
        #         return value
        if role == Qt.DecorationRole:
            if column == TutorialsModel.Columns.HAS_COVER.value:
                value = folder.cover
                return None if value else self.__no_cover_icon
            elif column == TutorialsModel.Columns.ONLINE.value:
                return None if folder.disk.online else self.__offline_icon
        elif role == Qt.CheckStateRole:
            if column == TutorialsModel.Columns.CHECKED.value:
                return Qt.Checked if folder.checked else Qt.Unchecked
        elif role == Qt.DisplayRole:
            if column == TutorialsModel.Columns.INDEX.value:
                return folder.id_
            elif column == TutorialsModel.Columns.DISK_NAME.value:
                return folder.disk.disk_name
            elif column == TutorialsModel.Columns.FOLDER_PARENT.value:
                return folder.folder_parent
            elif column == TutorialsModel.Columns.FOLDER_NAME.value:
                return folder.folder_name

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        row = index.row()

        folder = self.folder(row)

        if folder is None:
            return False

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == TutorialsModel.Columns.CHECKED.value:
                folder.checked = (value == Qt.Checked)
                dal.session.commit()
                del self.__cache[row]
                return True
        return False

    def flags(self, index: QModelIndex) -> Any:
        column = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | super().flags(index)

        if column == TutorialsModel.Columns.CHECKED.value:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def __filtered_and_sorted(self, query: Query) -> Query:
        if self.__only_show_checked_disks:
            query = query.filter(Disk.checked == True)  # noqa: E712

        # if len(self.__search_text):
        #     for key in self.__search_text.split():
        #         query = (
        #             query
        #             .filter((Disk.disk_parent + '/' + Disk.disk_name + '/' + Folder.folder_parent + '/' + Folder.folder_name)
        #             .like(f'%{key}%'))
        #         )

        # for publisher in dal.session.query(Publisher).filter(Publisher.search == Search.WITH):
        #     query = query.filter(Publisher.id_ == publisher.id_)

        # for publisher in dal.session.query(Publisher).filter(Publisher.search == Search.WITHOUT):
        #     query = query.filter(Publisher.id_ != publisher.id_)

        # for author in dal.session.query(Author).filter(Author.search == Search.WITH):
        #     query = query.filter(Author.id_ == author.id_)

        # for author in dal.session.query(Author).filter(Author.search == Search.WITHOUT):
        #     tutorials_with_author = dal.session.query(tutorial_author_table.c.tutorial_id).filter(tutorial_author_table.c.author_id == author.id_)
        #     query = query.filter(Tutorial.id_.not_in(tutorials_with_author))

        return query

    def __joined(self, query: Query) -> Query:
        # query = (
        #     query
        #     .join(Disk)
        #     .join(Tutorial)
        #     .join(Publisher)
        #     .join(tutorial_author_table)
        #     .join(Author)
        #     .filter(
        #         Folder.disk_id == Disk.id_,
        #         Folder.tutorial_id == Tutorial.id_,
        #         Tutorial.publisher_id == Publisher.id_,
        #         tutorial_author_table.c.tutorial_id == Tutorial.id_,
        #         tutorial_author_table.c.author_id == Author.id_
        #     )
        #     .group_by(Tutorial.id_)
        # )

        return query

    def __query(self) -> Query:
        # query = (
        #     dal
        #     .session
        #     .query(
        #         Folder.id_,
        #         Folder.folder_parent,
        #         Folder.folder_name,
        #         Folder.status,
        #         Folder.system_id,
        #         Folder.created,
        #         Folder.modified,
        #         Folder.size,
        #         Disk.online,
        #         Disk.disk_parent,
        #         Disk.disk_name,
        #         Disk.checked,
        #         TutorialsModel.Columns.CHECKED.column.label(TutorialsModel.Columns.CHECKED.alias),
        #         TutorialsModel.Columns.HAS_COVER.column.label(TutorialsModel.Columns.HAS_COVER.alias),
        #         TutorialsModel.Columns.PUBLISHER.column.label(TutorialsModel.Columns.PUBLISHER.alias),
        #         TutorialsModel.Columns.TITLE.column.label(TutorialsModel.Columns.TITLE.alias),
        #         TutorialsModel.Columns.AUTHORS.column.label(TutorialsModel.Columns.AUTHORS.alias),
        #     )
        # )

        query = (
            dal
            .session
            .query(Folder)
            .join(Disk)
        )

        return self.__filtered_and_sorted(self.__joined(query))

    def folder(self, row: int) -> Any:
        if row < 0 or row >= self.__row_count:
            return None

        data = self.__cache.get(row, None)

        if data is None:
            data = self.__folder(row)

        if data is None:
            return None

        self.__cache[row] = data

        return data

    def __folder(self, row: int) -> Any:
        query = self.__cached_query

        # column: Column = TutorialsModel.Columns(self.__sort_column).column
        # if column in [
        #     TutorialsModel.Columns.TITLE.column,
        #     TutorialsModel.Columns.PUBLISHER.column,
        #     TutorialsModel.Columns.AUTHORS.column,
        # ]:
        #     query = query.order_by(column.is_(None), column.is_(''))
        # column = column.asc() if self.__sort_ascending else column.desc()
        # query = query.order_by(column)
        # if column not in [Folder.folder_name, Folder.id_]:
        #     query = query.order_by(Folder.folder_name.asc())

        return query.offset(row).limit(1).first()

    def sort(self, index: int, sort_oder: Qt.SortOrder) -> None:
        self.beginResetModel()
        self.__sort_column = index
        self.__sort_ascending = (sort_oder == Qt.SortOrder.AscendingOrder)
        self.__cache.clear()
        self.endResetModel()

    def total_size(self) -> int:
        # if dal.session is None:
        #     return 0

        # folders_shown = self.__filtered(
        #     self.__joined(
        #         (
        #             dal
        #             .session
        #             .query(Folder.id_)
        #         )
        #     )
        # )

        # total_size = (
        #     dal
        #     .session
        #     .query(func.sum(Folder.size))
        #     .where(Folder.id_.in_(folders_shown))
        # ).scalar()

        # return total_size if total_size is not None else 0
        return 0

tutorials_model = TutorialsModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
