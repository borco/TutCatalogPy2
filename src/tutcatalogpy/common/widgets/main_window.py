from typing import Final, List

from PySide2.QtCore import QSettings, Qt
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QMainWindow, QStatusBar, QToolBar


class CommonMainWindow(QMainWindow):
    SETTINGS_GROUP: Final[str] = 'main_window'
    SETTINGS_WINDOW_GEOMETRY: Final[str] = 'geometry'
    SETTINGS_WINDOW_STATE: Final[str] = 'state'

    _docks: List = []
    _persistent_objects: List = []  # objects that save and load from settings

    def _setup_statusbar(self) -> None:
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

    def _setup_docks(self) -> None:
        self.setDockOptions(
            self.AllowNestedDocks |
            self.AllowTabbedDocks |
            self.GroupedDragging |
            self.VerticalTabs
        )

        for dock in self._docks:
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)
            dock.setup_dock()

    def _setup_toolbars(self) -> None:
        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('main_toolbar')
        self.addToolBar(self.__toolbar)

        for dock in self._docks:
            self.__toolbar.addActions(dock.toolbar_actions)

    def __save_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_WINDOW_GEOMETRY, self.saveGeometry())
        settings.setValue(self.SETTINGS_WINDOW_STATE, self.saveState())
        settings.endGroup()

        for po in self._persistent_objects:
            po.save_settings(settings)

    def __load_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        self.restoreGeometry(settings.value(self.SETTINGS_WINDOW_GEOMETRY, b''))
        self.restoreState(settings.value(self.SETTINGS_WINDOW_STATE, b''))
        settings.endGroup()

        for po in self._persistent_objects:
            po.load_settings(settings)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        self.__save_settings(settings)
        del settings
        super().closeEvent(event)

    def load_settings(self) -> None:
        settings = QSettings()
        self.__load_settings(settings)
        del settings
