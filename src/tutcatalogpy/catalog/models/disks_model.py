import logging
from typing import Any, Dict, Optional

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide2.QtGui import QBrush
from sqlalchemy.orm import Query
from sqlalchemy.sql.schema import Column

from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.widgets.db_table_column_enum import DbTableColumnEnum

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DisksModel(QAbstractTableModel):

    disk_checked_changed = Signal(int)

    class Columns(DbTableColumnEnum):
        CHECKED = (0, 'Checked', 'checked', Disk.checked)
        INDEX = (1, 'Index', 'index_', Disk.index_)
        NAME = (2, 'Name', 'disk_name', Disk.disk_name)
        PATH = (3, 'Path', 'disk_parent', Disk.disk_parent)
        LOCATION = (4, 'Location', 'location', Disk.location)
        ROLE = (5, 'Role', 'role', Disk.role)
        DEPTH = (6, 'Depth', 'depth', Disk.depth)

    def __init__(self) -> None:
        super().__init__()
        self.__cache: Dict[int, Any] = {}
        self.__row_count: int = 0
        self.__sort_column: int = 0
        self.__sort_ascending: bool = True

    def columnCount(self, index) -> int:
        return len(DisksModel.Columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Optional[Any]:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in [DisksModel.Columns.CHECKED.value, DisksModel.Columns.INDEX.value]:
                return ''
            else:
                return DisksModel.Columns(section).label

        return super().headerData(section, orientation, role)

    def rowCount(self, index) -> int:
        return self.__row_count

    def refresh(self) -> None:
        self.beginResetModel()
        self.__row_count = self.__query().count() if dal.connected else 0
        self.__cache.clear()
        self.endResetModel()
        log.debug('Disk model refreshed.')

    def data(self, index, role) -> Optional[Any]:
        row = index.row()

        disk = self.disk(row)

        if disk is None:
            return None

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == DisksModel.Columns.CHECKED.value:
                return Qt.Checked if disk.checked else Qt.Unchecked
        elif role == Qt.ForegroundRole:
            if column == DisksModel.Columns.NAME.value and not disk.online:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            if column == DisksModel.Columns.CHECKED.value:
                return ''
            return getattr(disk, DisksModel.Columns(column).alias)
        elif role == Qt.UserRole:
            return disk

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        row = index.row()

        disk = self.disk(row)

        if disk is None:
            return False

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == DisksModel.Columns.CHECKED.value:
                disk.checked = (value == Qt.Checked)
                self.disk_checked_changed.emit(row)
                dal.session.commit()
                return True
        return False

    def flags(self, index: QModelIndex) -> Any:
        column = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | super().flags(index)

        if column == DisksModel.Columns.CHECKED.value:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def __query(self) -> Query:
        query = (
            dal
            .session
            .query(Disk)
        )

        return query

    def disk(self, row) -> Optional[Any]:
        if row < 0 or row >= self.__row_count:
            return None

        data = self.__cache.get(row, None)

        if data is None:
            data = self.__disk(row)

        if data is None:
            return None

        self.__cache[row] = data

        return data

    def __disk(self, row: int) -> Any:
        query = self.__query()

        column: Column = DisksModel.Columns(self.__sort_column).column
        column = column.asc() if self.__sort_ascending else column.desc()
        query = query.order_by(column)
        if column != Disk.disk_name:
            query = query.order_by(Disk.disk_name.asc())

        return query.offset(row).limit(1).one()

    def sort(self, index: int, sort_oder: Qt.SortOrder) -> None:
        self.beginResetModel()
        self.__sort_column = index
        self.__sort_ascending = (sort_oder == Qt.SortOrder.AscendingOrder)
        self.__cache.clear()
        self.endResetModel()


disks_model = DisksModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
