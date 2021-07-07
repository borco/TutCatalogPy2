import enum
import logging
from typing import Any, Dict, Final, Optional

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide2.QtGui import QBrush, QIcon
from sqlalchemy.orm import Query
from sqlalchemy.sql.schema import Column

from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.files import relative_path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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

    CHECKED = (0, 'Checked', Disk.checked)
    INDEX = (1, 'Index', Disk.index_, 'index_')
    ONLINE = (2, 'Online', Disk.online)
    LOCATION = (3, 'Location', Disk.location)
    NAME = (4, 'Name', Disk.disk_name, 'disk_name')
    PATH = (5, 'Path', Disk.disk_parent, 'disk_parent')
    ROLE = (6, 'Role', Disk.role, 'role')
    DEPTH = (7, 'Depth', Disk.depth, 'depth')


class DisksModel(QAbstractTableModel):

    OFFLINE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/offline.svg')
    REMOTE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/remote.svg')

    disk_checked_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.__cache: Dict[int, Disk] = {}
        self.__row_count: int = 0
        self.__sort_column: int = 0
        self.__sort_ascending: bool = True

    def init_icons(self) -> None:
        self.__offline_icon = QIcon(self.OFFLINE_ICON)
        self.__remote_icon = QIcon(self.REMOTE_ICON)

    def columnCount(self, index) -> int:
        return len(Columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Optional[Any]:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in [Columns.CHECKED.value, Columns.INDEX.value]:
                return ''
            else:
                return Columns(section).label

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

        disk: Optional[Disk] = self.disk(row)

        if disk is None:
            return None

        column = index.column()

        if role == Qt.DecorationRole:
            if column == Columns.ONLINE.value:
                return None if disk.online else self.__offline_icon
            elif column == Columns.LOCATION.value:
                return None if disk.location == Disk.Location.LOCAL else self.__remote_icon
        elif role == Qt.CheckStateRole:
            if column == Columns.CHECKED.value:
                return Qt.Checked if disk.checked else Qt.Unchecked
        elif role == Qt.ForegroundRole:
            if column == Columns.NAME.value and not disk.online:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            if column in [
                Columns.CHECKED.value,
                Columns.ONLINE.value,
                Columns.LOCATION.value,
            ]:
                return None
            return getattr(disk, Columns(column).alias)
        elif role == Qt.UserRole:
            return disk

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        row = index.row()

        disk = self.disk(row)

        if disk is None:
            return False

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == Columns.CHECKED.value:
                disk.checked = (value == Qt.Checked)
                self.disk_checked_changed.emit(row)
                dal.session.commit()
                return True
        return False

    def flags(self, index: QModelIndex) -> Any:
        column = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | super().flags(index)

        if column == Columns.CHECKED.value:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def __query(self) -> Query:
        query = (
            dal
            .session
            .query(Disk)
        )

        return query

    def disk(self, row) -> Optional[Disk]:
        if row < 0 or row >= self.__row_count:
            return None

        disk = self.__cache.get(row, None)

        if disk is None:
            disk = self.__disk(row)

        if disk is None:
            return None

        self.__cache[row] = disk

        return disk

    def __disk(self, row: int) -> Disk:
        query = self.__query()

        column: Column = Columns(self.__sort_column).column
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
