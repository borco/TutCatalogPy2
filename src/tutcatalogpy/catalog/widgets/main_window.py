import logging
from typing import Final, List, Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QFileDialog, QFrame, QLabel, QMenu, QMenuBar

from tutcatalogpy.catalog.config import config
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.recent_files import RecentFiles
from tutcatalogpy.common.widgets.logging_dock import LoggingDock
from tutcatalogpy.common.widgets.main_window import CommonMainWindow

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MainWindow(CommonMainWindow):
    WINDOW_TITLE: Final[str] = 'TutCatalogPy2 Catalog'
    WINDOW_ICON_FILE: Final[str] = relative_path(__file__, '../../resources/icons/catalog.png')

    FILE_MENU: Final[str] = 'File'

    FILE_OPEN_MENU: Final[str] = 'Open...'
    FILE_OPEN_SHORTCUT: Final[QKeySequence] = QKeySequence.Open
    FILE_OPEN_TIP: Final[str] = 'Open config ...'

    FILE_OPEN_DIALOG_TITLE: Final[str] = 'Open TutCatalogPy config file'
    FILE_OPEN_DIALOG_FILTERS: Final[List[str]] = [
        'TutCatalogPy config files (*.yml)',
        'Any Files (*)'
    ]

    FILE_QUIT_MENU: Final[str] = 'Quit'
    FILE_QUIT_SHORTCUT: Final[QKeySequence] = QKeySequence.Quit

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.WINDOW_TITLE)

        self.__recent_files = RecentFiles(self)

        self.__connect_objects()
        self._setup_statusbar()
        self._setup_docks()
        self.__setup_menus()
        self._setup_toolbars()

        self._persistent_objects += [
            self.__recent_files
        ]
        self._persistent_objects += self._docks

    def __connect_objects(self) -> None:
        config.loaded.connect(self.__on_config_loaded)

    def _setup_statusbar(self) -> None:
        super()._setup_statusbar()

        self.__folder_summary = QLabel()
        self.__folder_summary.setFrameShape(QFrame.StyledPanel)
        self.__folder_summary.setMinimumWidth(200)
        self._statusbar.addPermanentWidget(self.__folder_summary)

    def _setup_docks(self) -> None:
        class CatalogLoggingDock(LoggingDock):
            _show_sql = True

        self.__log_dock = CatalogLoggingDock()

        self._docks = [
            self.__log_dock,
        ]

        super()._setup_docks()

    def __setup_menus(self) -> None:
        self.__menubar = QMenuBar()
        self.setMenuBar(self.__menubar)

        # self.__menubar.setNativeMenuBar(False)

        # File Menu
        menu = QMenu(self.FILE_MENU, self)

        action = QAction(self.FILE_OPEN_MENU, self)
        action.setShortcut(self.FILE_OPEN_SHORTCUT)
        action.setStatusTip(self.FILE_OPEN_TIP)
        action.triggered.connect(self.__open_config)
        menu.addAction(action)

        self.__recent_files.triggered.connect(self.load_config)
        menu.addMenu(self.__recent_files.menu)

        action = QAction(self.FILE_QUIT_MENU, self)
        action.setShortcut(self.FILE_QUIT_SHORTCUT)
        action.setMenuRole(QAction.QuitRole)
        action.triggered.connect(self.close)
        menu.addAction(action)

        self.__menubar.addMenu(menu)

        # Views Menu
        menu = QMenu('Docks', self)

        for dock in self._docks:
            menu.addAction(dock.toggleViewAction())

        self.__menubar.addMenu(menu)

    def load_config(self, file_name: Optional[str] = None) -> None:
        config.load(file_name)

    def __open_config(self) -> None:
        dialog = QFileDialog(self, Qt.Sheet)
        dialog.setWindowTitle(self.FILE_OPEN_DIALOG_TITLE)
        dialog.setNameFilters(self.FILE_OPEN_DIALOG_FILTERS)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)

        if dialog.exec_():
            if len(dialog.selectedFiles()) == 1:
                config.load(dialog.selectedFiles()[0])

    def __on_config_loaded(self) -> None:
        if config.file_name is not None:
            self.__recent_files.add_file(config.file_name)
            self.setWindowTitle(f'{config.file_name} - {self.WINDOW_TITLE}')
        else:
            self.setWindowTitle(self.WINDOW_TITLE)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
