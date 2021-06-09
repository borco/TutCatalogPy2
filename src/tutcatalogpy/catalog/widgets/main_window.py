import logging
from typing import Final, List, Optional

from PySide2.QtCore import QSize, QTimer, Qt
from PySide2.QtGui import QCloseEvent, QIcon, QKeySequence
from PySide2.QtWidgets import QAction, QFileDialog, QFrame, QLabel, QMenu, QMenuBar, QToolBar

from tutcatalogpy.catalog.config import config
from tutcatalogpy.catalog.models.disks_model import disks_model
from tutcatalogpy.catalog.scan_controller import scan_controller
from tutcatalogpy.catalog.widgets.disks_dock import DisksDock
from tutcatalogpy.catalog.widgets.scan_config_dock import ScanConfigDock
from tutcatalogpy.catalog.widgets.scan_dialog import ScanDialog
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

        disks_model.setParent(self)

        self.__recent_files = RecentFiles(self)

        self.__connect_objects()
        self._setup_statusbar()
        self._setup_docks()
        self.__setup_actions()
        self.__setup_menus()
        self.__setup_controllers()
        self.__setup_dialogs()
        self.__setup_toolbars()

        self._persistent_objects += [
            self.__recent_files,
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

        self.__disks_dock = DisksDock()
        self.__disks_dock.set_model(disks_model)

        self.__log_dock = CatalogLoggingDock()

        self.__scan_config_dock = ScanConfigDock()

        self._docks = [
            self.__disks_dock,
            self.__log_dock,
            self.__scan_config_dock,
        ]

        super()._setup_docks()

    def __setup_actions(self) -> None:
        self.__scan_startup_action = QAction()
        self.__scan_startup_action.setStatusTip('Startup scan')
        self.__scan_startup_action.setIcon(QIcon(relative_path(__file__, '../../resources/icons/scan_startup.svg')))
        self.__scan_startup_action.triggered.connect(self.__on_scan_startup_action_triggered)

        self.__scan_normal_action = QAction()
        self.__scan_normal_action.setStatusTip('Normal scan')
        self.__scan_normal_action.setIcon(QIcon(relative_path(__file__, '../../resources/icons/scan.svg')))
        self.__scan_normal_action.triggered.connect(self.__on_scan_normal_action_triggered)

        self.__scan_extended_action = QAction()
        self.__scan_extended_action.setStatusTip('Extended scan')
        self.__scan_extended_action.setIcon(QIcon(relative_path(__file__, '../../resources/icons/scan_more.svg')))
        self.__scan_extended_action.triggered.connect(self.__on_scan_extended_action_triggered)

        self.__scan_actions = [
            self.__scan_startup_action,
            self.__scan_normal_action,
            self.__scan_extended_action,
        ]

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

        self.__recent_files.triggered.connect(self.__load_config)
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

    def __setup_controllers(self) -> None:
        scan_controller.setParent(self)
        scan_controller.setup()
        scan_worker = scan_controller.worker
        scan_worker.scan_started.connect(self.__on_scan_worker_scan_started)
        scan_worker.scan_finished.connect(self.__on_scan_worker_scan_finished)

    def __setup_toolbars(self) -> None:
        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('main_toolbar')
        self.__toolbar.setIconSize(QSize(self.DOCK_ICON_SIZE, self.DOCK_ICON_SIZE))
        self.addToolBar(self.__toolbar)

        self.__toolbar.addActions([
            self.__scan_startup_action,
            self.__scan_normal_action,
            self.__scan_extended_action
        ])

        self._setup_docks_toolbar()

    def __cleanup_controllers(self) -> None:
        scan_controller.cleanup()

    def __setup_dialogs(self) -> None:
        self.__scan_dialog: Optional[ScanDialog] = None
        self.__scan_dialog = ScanDialog(parent=self)
        self.__scan_dialog.set_scan_worker(scan_controller.worker)
        self.__scan_dialog.finished.connect(self.__on_scan_dialog_finished)

    def __on_scan_startup_action_triggered(self) -> None:
        scan_controller.scan_startup()

    def __on_scan_normal_action_triggered(self) -> None:
        scan_controller.scan_normal()

    def __on_scan_extended_action_triggered(self) -> None:
        scan_controller.scan_extended()

    def __on_scan_worker_scan_started(self) -> None:
        for action in self.__scan_actions:
            action.setEnabled(False)

        self.__scan_dialog.reset()
        self.__scan_dialog.show()
        QTimer.singleShot(500, self.__check_scan_finished_too_quickly)

    def __on_scan_worker_scan_finished(self) -> None:
        disks_model.refresh()

    def __check_scan_finished_too_quickly(self) -> None:
        if self.__scan_dialog and not scan_controller.worker.scanning:
            log.debug('Scan finished extremely quickly!')
            self.__scan_dialog.accept()
        else:
            log.debug('Still scanning...')

    def __on_scan_dialog_finished(self) -> None:
        for action in self.__scan_actions:
            action.setEnabled(True)

    def __load_config(self, file_name: Optional[str] = None) -> None:
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

        disks_model.refresh()

    def show(self) -> None:
        super().show()
        self.__load_config(self.__recent_files.most_recent_file)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.__cleanup_controllers()
        super().closeEvent(event)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
