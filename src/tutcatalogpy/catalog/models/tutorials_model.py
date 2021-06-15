import logging
from typing import Any, Dict, Optional

from PySide2.QtCore import QAbstractTableModel, QDateTime, Qt
from PySide2.QtGui import QIcon
from humanize import naturalsize
from sqlalchemy.orm import Query
from sqlalchemy.sql.schema import Column

from tutcatalogpy.catalog.db.cover import Cover
from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
from tutcatalogpy.catalog.db.folder import Folder
from tutcatalogpy.catalog.widgets.search_dock import SearchDock
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.db_table_column_enum import DbTableColumnEnum

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TutorialsModel(QAbstractTableModel):

    class Columns(DbTableColumnEnum):
        INDEX = (0, 'Index', 'id_', Folder.id_)
        DISK_NAME = (1, 'Disk', 'disk_name', Disk.disk_name)
        FOLDER_PARENT = (2, 'Folder Parent', 'folder_parent', Folder.folder_parent)
        FOLDER_NAME = (3, 'Folder Name', 'folder_name', Folder.folder_name)
        HAS_COVER = (4, 'Cover', 'has_cover', (Cover.size != None))
        SIZE = (5, 'Size', 'size', Folder.size)
        CREATED = (6, 'Created', 'created', Folder.created)
        MODIFIED = (7, 'Modified', 'modified', Folder.modified)

    NO_COVER_ICON = relative_path(__file__, '../../resources/icons/no_cover.svg')

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
            if section in [TutorialsModel.Columns.INDEX.value]:
                return ''
            else:
                return TutorialsModel.Columns(section).label

    def rowCount(self, index) -> int:
        return self.__row_count

    def refresh(self) -> None:
        self.beginResetModel()
        self.__row_count = self.__query().count() if dal.connected else 0
        self.__cache.clear()
        self.endResetModel()
        log.debug('Folder model updated row count: %s.', self.__row_count)

    def data(self, index, role) -> Any:
        row = index.row()

        tutorial = self.tutorial(row)

        if tutorial is None:
            return None

        column = index.column()

        if role == Qt.DecorationRole:
            if column == TutorialsModel.Columns.HAS_COVER.value:
                value = getattr(tutorial, TutorialsModel.Columns(column).attr)
                return None if value else self.__no_cover_icon
        elif role == Qt.DisplayRole:
            value = getattr(tutorial, TutorialsModel.Columns(column).attr)
            if column == TutorialsModel.Columns.SIZE.value:
                return naturalsize(value) if value else ''
            elif column == TutorialsModel.Columns.HAS_COVER.value:
                return None
            elif column in [TutorialsModel.Columns.CREATED.value, TutorialsModel.Columns.MODIFIED.value]:
                return QDateTime.fromSecsSinceEpoch(value.timestamp())
            else:
                return value

    def __filtered(self, query: Query) -> Query:
        if self.__only_show_checked_disks:
            query = query.filter(Disk.checked == True)  # noqa: E712

        if len(self.__search_text):
            for key in self.__search_text.split():
                query = (
                    query
                    .filter((Disk.disk_parent + '/' + Disk.disk_name + '/' + Folder.folder_parent + '/' + Folder.folder_name)
                    .like(f'%{key}%'))
                )

        return query

    def __query(self) -> Query:
        query = (
            dal
            .session
            .query(
                Folder.id_,
                Folder.folder_parent,
                Folder.folder_name,
                Folder.status,
                Folder.system_id,
                Folder.created,
                Folder.modified,
                Folder.size,
                Disk.disk_parent,
                Disk.disk_name,
                Disk.checked,
                (Cover.size != None).label('has_cover'),
            )
            .join(Disk, Folder.disk_id == Disk.id_)
            .join(Cover, Cover.folder_id == Folder.id_)
        )

        return self.__filtered(query)

    def tutorial(self, row: int) -> Any:
        if row < 0 or row >= self.__row_count:
            return None

        data = self.__cache.get(row, None)

        if data is None:
            data = self.__tutorial(row)

        if data is None:
            return None

        self.__cache[row] = data

        return data

    def __tutorial(self, row: int) -> Any:
        query = self.__query()

        column: Column = TutorialsModel.Columns(self.__sort_column).column
        column = column.asc() if self.__sort_ascending else column.desc()
        query = query.order_by(column)
        if column not in [Folder.folder_name, Folder.id_]:
            query = query.order_by(Folder.folder_name.asc())

        return query.offset(row).limit(1).first()

    def sort(self, index: int, sort_oder: Qt.SortOrder) -> None:
        self.beginResetModel()
        self.__sort_column = index
        self.__sort_ascending = (sort_oder == Qt.SortOrder.AscendingOrder)
        self.__cache.clear()
        self.endResetModel()


tutorials_model = TutorialsModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
