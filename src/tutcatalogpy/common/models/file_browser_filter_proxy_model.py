from enum import IntEnum

from natsort import os_sorted
from PySide2.QtCore import QModelIndex, QSortFilterProxyModel, Qt
from PySide2.QtWidgets import QFileSystemModel


class FileBrowserFilterProxyModel(QSortFilterProxyModel):
    class Column(IntEnum):
        NAME = 0
        SIZE = 1
        KIND = 2
        MODIFIED = 3

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        def sort_by_name(ascending, left_info, right_info):
            left_name = left_info.fileName().lower()
            right_name = right_info.fileName().lower()
            s = os_sorted((left_name, right_name), reverse=not ascending)
            return s[0] == left_name

        fsm: QFileSystemModel = self.sourceModel()
        if fsm is not None:
            column = self.sortColumn()
            ascending = (self.sortOrder() == Qt.AscendingOrder)
            left_info = fsm.fileInfo(left)
            right_info = fsm.fileInfo(right)

            if column == self.Column.NAME.value:
                if left_info.isDir() and not right_info.isDir():
                    return ascending
                elif not left_info.isDir() and right_info.isDir():
                    return not ascending
                else:
                    return sort_by_name(True, left_info, right_info)

            elif column == self.Column.SIZE.value:
                if left_info.isDir() and not right_info.isDir():
                    return True
                elif not left_info.isDir() and right_info.isDir():
                    return False
                elif left_info.isDir() and right_info.isDir():
                    return sort_by_name(ascending, left_info, right_info)
                else:
                    left_size = left_info.size()
                    right_size = right_info.size()
                    if left_size == right_size:
                        return sort_by_name(ascending, left_info, right_info)
                    return left_size < right_size

        return super().lessThan(left, right)


if __name__ == '__main__':
    from tutcatalogpy.viewer.main import run
    run()
