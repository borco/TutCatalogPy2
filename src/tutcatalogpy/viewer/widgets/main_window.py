from PySide2.QtCore import QSettings, Qt
from PySide2.QtWidgets import QStatusBar, QToolBar

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.logging_dock import LoggingDock
from tutcatalogpy.common.widgets.main_window import CommonMainWindow


class MainWindow(CommonMainWindow):
    WINDOW_TITLE = 'TutCatalogPy2 Viewer'
    WINDOW_ICON_FILE = relative_path(__file__, '../../resources/icons/viewer.png')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__setup_statusbar()
        self.__setup_docks()
        self.__setup_toolbars()

    def __setup_statusbar(self) -> None:
        self.__statusbar = QStatusBar()
        self.setStatusBar(self.__statusbar)

    def __setup_docks(self) -> None:
        self.setDockOptions(
            self.AllowNestedDocks |
            self.AllowTabbedDocks |
            self.GroupedDragging |
            self.VerticalTabs
        )

        self.__log_dock = LoggingDock()

        self.__docks = [
            self.__log_dock,
        ]

        for dock in self.__docks:
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)
            dock.setup_dock()

    def __setup_toolbars(self) -> None:
        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('main_toolbar')
        self.addToolBar(self.__toolbar)

        for dock in self.__docks:
            self.__toolbar.addActions(dock.toolbar_actions)

    def _save_settings(self, settings: QSettings) -> None:
        super()._save_settings(settings)

        for dock in self.__docks:
            dock.save_settings(settings)

    def _load_settings(self, settings: QSettings) -> None:
        super()._load_settings(settings)

        for dock in self.__docks:
            dock.load_settings(settings)


if __name__ == '__main__':
    from tutcatalogpy.viewer.main import run
    run()
