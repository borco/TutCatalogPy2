import logging
from typing import Any, Dict

from PySide2.QtCore import QAbstractTableModel, QDateTime, Qt, Slot
from humanize import naturalsize
from sqlalchemy.orm import Query
from sqlalchemy.sql.schema import Column

from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
from tutcatalogpy.catalog.db.folder import Folder
from tutcatalogpy.catalog.widgets.search_dock import SearchDock
from tutcatalogpy.common.widgets.db_table_column_enum import DbTableColumnEnum


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TutorialsModel(QAbstractTableModel):

    class Columns(DbTableColumnEnum):
        INDEX = (0, 'Index', 'id_', Folder.id_)
        DISK_NAME = (1, 'Disk', 'disk_name', Disk.disk_name)
        FOLDER_PARENT = (2, 'Folder Parent', 'folder_parent', Folder.folder_parent)
        FOLDER_NAME = (3, 'Folder Name', 'folder_name', Folder.folder_name)
        SIZE = (4, 'Size', 'size', Folder.size)
        CREATED = (5, 'Created', 'created', Folder.created)
        MODIFIED = (6, 'Modified', 'modified', Folder.modified)

    def __init__(self):
        super().__init__()
        self.__cache: Dict[int, Any] = {}
        self.__row_count: int = 0
        self.__sort_column: int = 0
        self.__sort_ascending: bool = True

    @Slot()
    def search(self) -> None:
        dock: SearchDock = self.sender()
        log.info(f"search: text: '{dock.text}', only show checked disks: {dock.only_show_checked_disks}")

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

        if role == Qt.DisplayRole:
            value = getattr(tutorial, TutorialsModel.Columns(column).attr)
            if column == TutorialsModel.Columns.SIZE.value:
                return naturalsize(value) if value else ''
            elif column in [TutorialsModel.Columns.CREATED.value, TutorialsModel.Columns.MODIFIED.value]:
                return QDateTime.fromSecsSinceEpoch(value.timestamp())
            else:
                return value

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
            )
            .join(Disk, Folder.disk_id == Disk.id_)
        )

        return query

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
        if column != Folder.folder_name and Folder.id_:
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
