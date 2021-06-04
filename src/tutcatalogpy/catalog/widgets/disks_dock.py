import logging
from typing import Final

from PySide2.QtCore import QByteArray, QSettings
from PySide2.QtWidgets import QTableView, QVBoxLayout, QWidget

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DisksDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'disk_dock'
    SETTINGS_HEADER_STATE: Final[str] = 'header_state'
    SETTINGS_DETAILS_VISIBLE: Final[str] = 'details_visible'

    DOCK_TITLE: Final[str] = 'Disks'
    DOCK_OBJECT_NAME: Final[str] = 'disk_dock'

    DISK_VIEW_OBJECT_NAME: Final[str] = 'disks_view'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/disks.svg')
    _dock_status_tip: Final[str] = 'Toggle disks dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self._setup_dock_toolbar()

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.__disk_view = QTableView()
        layout.addWidget(self.__disk_view)
        self.__disk_view.setObjectName(self.DISK_VIEW_OBJECT_NAME)
        self.__disk_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__disk_view.horizontalHeader().setStretchLastSection(True)
        self.__disk_view.verticalHeader().setVisible(False)

    def set_model(self, model) -> None:
        self.__disk_view.setModel(model)

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_HEADER_STATE, self.__disk_view.horizontalHeader().saveState())
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        self.__disk_view.horizontalHeader().restoreState(QByteArray(settings.value(self.SETTINGS_HEADER_STATE, b'')))
        settings.endGroup()

    def clear(self):
        pass


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
