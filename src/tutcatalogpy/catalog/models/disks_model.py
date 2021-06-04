import logging
from typing import Any, Dict, Optional

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide2.QtGui import QBrush

from sqlalchemy.sql.functions import func
from sqlalchemy.orm import Query

from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
from tutcatalogpy.common.labeled_enum import LabeledEnum

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DisksModel(QAbstractTableModel):

    disk_enabled_changed = Signal(int)

    class Columns(LabeledEnum):
        ENABLED = (0, '')
        INDEX = (1, 'Index')
        NAME = (2, 'Name')
        PATH = (3, 'Path')
        LOCATION = (4, 'Location')
        ROLE = (5, 'Role')
        DEPTH = (6, 'Depth')

    def __init__(self) -> None:
        super().__init__()
        self.__cache: Dict[int, Any] = {}
        self.__row_count: int = 0

    def columnCount(self, index) -> int:
        return len(DisksModel.Columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Optional[Any]:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return DisksModel.Columns(section).label

    def rowCount(self, index) -> int:
        return self.__row_count

    def refresh(self) -> None:
        self.beginResetModel()
        self.__row_count = dal.session.query(func.count(Disk.id_)).scalar() if dal.connected else 0
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
            if column == DisksModel.Columns.ENABLED.value:
                return Qt.Checked if disk.enabled else Qt.Unchecked
        elif role == Qt.ForegroundRole:
            if column == DisksModel.Columns.NAME.value and not disk.online:
                return QBrush(Qt.red)
        elif role == Qt.DisplayRole:
            if column == DisksModel.Columns.INDEX.value:
                return disk.index_ + 1
            elif column == DisksModel.Columns.NAME.value:
                return disk.path_name
            elif column == DisksModel.Columns.PATH.value:
                return disk.path_parent
            elif column == DisksModel.Columns.LOCATION.value:
                return disk.location
            elif column == DisksModel.Columns.ROLE.value:
                return disk.role
            elif column == DisksModel.Columns.DEPTH.value:
                return disk.depth
        elif role == Qt.UserRole:
            return disk

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        row = index.row()

        disk = self.disk(row)

        if disk is None:
            return False

        column = index.column()

        if role == Qt.CheckStateRole:
            if column == DisksModel.Columns.ENABLED.value:
                disk.enabled = (value == Qt.Checked)
                self.disk_enabled_changed.emit(row)
                dal.session.commit()
                return True
        return False

    def flags(self, index: QModelIndex) -> Any:
        column = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if column == DisksModel.Columns.ENABLED.value:
            flags |= Qt.ItemIsUserCheckable

        return flags

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

    def __query(self) -> Query:
        query = (
            dal
            .session
            .query(Disk)
        )

        return query

    def __disk(self, row: int) -> Any:
        query = self.__query()

        # TODO: do the sorting

        return query.offset(row).limit(1).one()


disks_model = DisksModel()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
