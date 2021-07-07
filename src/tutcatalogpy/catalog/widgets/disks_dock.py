import logging
from typing import Final

from PySide2.QtCore import QByteArray, QSettings, Qt
from PySide2.QtWidgets import QAction, QMenu, QTableView

from tutcatalogpy.catalog.models.disks_model import Columns
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DisksDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'disk_dock'
    SETTINGS_HEADER_STATE: Final[str] = 'header_state'
    SETTINGS_VERTICAL_HEADER_VISIBLE: Final[str] = 'vertical_header_visible'

    DOCK_TITLE: Final[str] = 'Disks'
    DOCK_OBJECT_NAME: Final[str] = 'disk_dock'

    DISKS_VIEW_OBJECT_NAME: Final[str] = 'disks_view'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/disks.svg')
    _dock_status_tip: Final[str] = 'Toggle disks dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        self.__disks_view = QTableView()
        self.__disks_view.setObjectName(self.DISKS_VIEW_OBJECT_NAME)
        self.__disks_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__disks_view.setSortingEnabled(True)

        self.__disks_view.verticalHeader().setVisible(False)

        horizontal_header = self.__disks_view.horizontalHeader()
        # NOTE: if you can't move sections, try to delete the settings .ini file
        horizontal_header.setSectionsMovable(True)
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSortIndicatorShown(True)
        horizontal_header.setContextMenuPolicy(Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(self.__on_header_context_menu_requested)

        self.setWidget(self.__disks_view)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def __setup_header_context_menu(self) -> None:
        header = self.__disks_view.horizontalHeader()
        menu = QMenu(self)

        # vertical header
        label = 'Row Number'
        action = QAction(label, menu)
        action.setData(None)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(self.__on_header_context_menu_triggered)
        menu.addAction(action)
        self.__vertical_header_visible_action = action

        # other columns
        for section in range(len(Columns)):
            label = Columns(section).label
            action = QAction(label, menu)
            action.setData(section)
            action.setCheckable(True)
            action.setChecked(not header.isSectionHidden(section))
            action.triggered.connect(self.__on_header_context_menu_triggered)
            menu.addAction(action)
        self.__context_menu = menu

    def __on_header_context_menu_requested(self, pos):
        self.__context_menu.exec_(self.__disks_view.mapToGlobal(pos))

    def __on_header_context_menu_triggered(self, checked):
        if self.sender().data() is None:
            header = self.__disks_view.verticalHeader()
            header.setVisible(checked)
        else:
            header = self.__disks_view.horizontalHeader()
            header.setSectionHidden(self.sender().data(), not checked)

    def set_model(self, model) -> None:
        self.__disks_view.setModel(model)

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_HEADER_STATE, self.__disks_view.horizontalHeader().saveState())
        settings.setValue(self.SETTINGS_VERTICAL_HEADER_VISIBLE, self.__disks_view.verticalHeader().isVisible())
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        self.__disks_view.horizontalHeader().restoreState(QByteArray(settings.value(self.SETTINGS_HEADER_STATE, b'')))
        vertical_header_visible = settings.value(self.SETTINGS_VERTICAL_HEADER_VISIBLE, True, type=bool)
        settings.endGroup()

        self.__setup_header_context_menu()
        self.__disks_view.verticalHeader().setVisible(vertical_header_visible)
        self.__vertical_header_visible_action.setChecked(vertical_header_visible)

    def clear(self):
        pass


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
