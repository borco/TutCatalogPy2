from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFrame, QLabel, QStatusBar, QToolBar

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.logging_dock import LoggingDock
from tutcatalogpy.common.widgets.main_window import CommonMainWindow


class MainWindow(CommonMainWindow):
    WINDOW_TITLE = 'TutCatalogPy2 Catalog'
    WINDOW_ICON_FILE = relative_path(__file__, '../../resources/icons/catalog.png')

    class __LoggingDock(LoggingDock):
        show_sql = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__setup_statusbar()
        self.__setup_docks()
        self.__setup_toolbars()

    def __setup_statusbar(self) -> None:
        self.__statusbar = QStatusBar()
        self.setStatusBar(self.__statusbar)

        self.__folder_summary = QLabel()
        self.__folder_summary.setFrameShape(QFrame.StyledPanel)
        self.__folder_summary.setMinimumWidth(200)
        self.__statusbar.addPermanentWidget(self.__folder_summary)

    def __setup_docks(self) -> None:
        self.setDockOptions(
            self.AllowNestedDocks |
            self.AllowTabbedDocks |
            self.GroupedDragging |
            self.VerticalTabs
        )

        self.__log_dock = self.__LoggingDock()

        self.__docks = [
            self.__log_dock,
        ]

        for dock in self.__docks:
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)
            dock.statusbar = self.statusBar()
            dock.setup_dock()

    def __setup_toolbars(self) -> None:
        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('main_toolbar')
        self.addToolBar(self.__toolbar)

        for dock in self.__docks:
            self.__toolbar.addActions(dock.toolbar_actions)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
