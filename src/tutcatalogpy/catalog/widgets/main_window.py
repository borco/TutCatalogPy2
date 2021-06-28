import logging
from pathlib import Path
from typing import Final, List, Optional

from PySide2.QtCore import QModelIndex, QSize, QTimer, QUrl, Qt
from PySide2.QtGui import QCloseEvent, QDesktopServices, QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import QAction, QFileDialog, QFrame, QLabel, QMenu, QMenuBar, QToolBar

from tutcatalogpy.catalog.config import config
from tutcatalogpy.catalog.models.disks_model import disks_model
from tutcatalogpy.catalog.models.tags_model import tags_model
from tutcatalogpy.catalog.models.tutorials_model import tutorials_model
from tutcatalogpy.catalog.scan_controller import scan_controller
from tutcatalogpy.catalog.widgets.cover_dock import CoverDock
from tutcatalogpy.catalog.widgets.disks_dock import DisksDock
from tutcatalogpy.catalog.widgets.scan_config_dock import ScanConfigDock
from tutcatalogpy.catalog.widgets.scan_dialog import ScanDialog
from tutcatalogpy.catalog.widgets.search_dock import SearchDock
from tutcatalogpy.catalog.widgets.tags_dock import TagsDock
from tutcatalogpy.catalog.widgets.tutorials_dock import TutorialsDock
from tutcatalogpy.common.db.cover import Cover
from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.disk import Disk
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.recent_files import RecentFiles
from tutcatalogpy.common.widgets.file_browser_dock import FileBrowserDock
from tutcatalogpy.common.widgets.info_tc_dock import InfoTcDock
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

    SCAN_TOOLBAR_OBJECT_NAME: Final[str] = 'scan_toolbar'

    SCAN_STARTUP_ICON: Final[str] = relative_path(__file__, '../../resources/icons/scan_startup.svg')
    SCAN_STARTUP_TIP: Final[str] = 'Startup scan'
    SCAN_NORMAL_ICON: Final[str] = relative_path(__file__, '../../resources/icons/scan.svg')
    SCAN_NORMAL_TIP: Final[str] = 'Normal scan'
    SCAN_EXTENDED_ICON: Final[str] = relative_path(__file__, '../../resources/icons/scan_more.svg')
    SCAN_EXTENDED_TIP: Final[str] = 'Extended scan'

    FOLDER_TOOLBAR_OBJECT_NAME: Final[str] = 'folder_toolbar'

    OPEN_FOLDER_ICON: Final[str] = relative_path(__file__, '../../resources/icons/open_folder.svg')
    OPEN_FOLDER_TIP: Final[str] = 'Open folder in external file browser'
    OPEN_TC_ICON: Final[str] = relative_path(__file__, '../../resources/icons/open_info_tc.svg')
    OPEN_TC_TIP: Final[str] = 'Open info.tc in external viewer'

    __current_folder_id: Optional[int] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.WINDOW_TITLE)

        disks_model.setParent(self)
        disks_model.init_icons()

        tutorials_model.setParent(self)
        tutorials_model.init_icons()

        self.__recent_files = RecentFiles(self)

        self._setup_statusbar()
        self._setup_docks()
        self.__setup_actions()
        self.__setup_menus()
        self.__setup_controllers()
        self.__setup_dialogs()
        self.__setup_toolbars()
        self.__setup_connections()

        self._persistent_objects += [
            self.__recent_files,
        ]
        self._persistent_objects += self._docks

    def _setup_statusbar(self) -> None:
        super()._setup_statusbar()

        self.__tutorials_summary = QLabel()
        self.__tutorials_summary.setFrameShape(QFrame.StyledPanel)
        self.__tutorials_summary.setMinimumWidth(150)
        self._statusbar.addPermanentWidget(self.__tutorials_summary)

    def _setup_docks(self) -> None:
        class CatalogLoggingDock(LoggingDock):
            _show_sql = True

        self.__search_dock = SearchDock()

        self.__disks_dock = DisksDock()
        self.__disks_dock.set_model(disks_model)

        self.__tutorials_dock = TutorialsDock()
        self.__tutorials_dock.set_model(tutorials_model)

        self.__info_tc_dock = InfoTcDock()

        self.__cover_dock = CoverDock()

        self.__tags_dock = TagsDock()
        self.__tags_dock.set_model(tags_model)
        self.__tags_dock.view.activated.connect(self.__on_tags_dock_view_activated)

        self.__file_browser_dock = FileBrowserDock()

        self.__log_dock = CatalogLoggingDock()

        self.__scan_config_dock = ScanConfigDock()

        self._docks = [
            self.__search_dock,
            self.__disks_dock,
            self.__tutorials_dock,
            self.__info_tc_dock,
            self.__cover_dock,
            self.__tags_dock,
            self.__file_browser_dock,
            self.__log_dock,
            self.__scan_config_dock,
        ]

        super()._setup_docks()

    def __setup_actions(self) -> None:
        self.__scan_startup_action = QAction()
        self.__scan_startup_action.setStatusTip(self.SCAN_STARTUP_TIP)
        self.__scan_startup_action.setIcon(QIcon(self.SCAN_STARTUP_ICON))
        self.__scan_startup_action.triggered.connect(self.__on_scan_startup_action_triggered)

        self.__scan_normal_action = QAction()
        self.__scan_normal_action.setStatusTip(self.SCAN_NORMAL_TIP)
        self.__scan_normal_action.setIcon(QIcon(self.SCAN_NORMAL_ICON))
        self.__scan_normal_action.triggered.connect(self.__on_scan_normal_action_triggered)

        self.__scan_extended_action = QAction()
        self.__scan_extended_action.setStatusTip(self.SCAN_EXTENDED_TIP)
        self.__scan_extended_action.setIcon(QIcon(self.SCAN_EXTENDED_ICON))
        self.__scan_extended_action.triggered.connect(self.__on_scan_extended_action_triggered)

        self.__open_folder_action = QAction()
        self.__open_folder_action.setIcon(QIcon(self.OPEN_FOLDER_ICON))
        self.__open_folder_action.setStatusTip(self.OPEN_FOLDER_TIP)
        self.__open_folder_action.triggered.connect(self.__on_open_folder_triggered)

        self.__open_tc_action = QAction()
        self.__open_tc_action.setIcon(QIcon(self.OPEN_TC_ICON))
        self.__open_tc_action.setStatusTip(self.OPEN_TC_TIP)
        self.__open_tc_action.triggered.connect(self.__on_open_tc_triggered)

        self.__scan_actions = [
            self.__scan_startup_action,
            self.__scan_normal_action,
            self.__scan_extended_action,
        ]

        self.__folder_actions = [
            self.__open_folder_action,
            self.__open_tc_action,
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

    def __setup_toolbars(self) -> None:
        self.__scan_toolbar = QToolBar()
        self.__scan_toolbar.setObjectName(self.SCAN_TOOLBAR_OBJECT_NAME)
        self.__scan_toolbar.setIconSize(QSize(self.DOCK_ICON_SIZE, self.DOCK_ICON_SIZE))
        self.addToolBar(self.__scan_toolbar)

        self.__folder_toolbar = QToolBar()
        self.__folder_toolbar.setObjectName(self.FOLDER_TOOLBAR_OBJECT_NAME)
        self.__folder_toolbar.setIconSize(QSize(self.DOCK_ICON_SIZE, self.DOCK_ICON_SIZE))
        self.addToolBar(self.__folder_toolbar)

        self.__scan_toolbar.addActions(self.__scan_actions)
        self.__folder_toolbar.addActions(self.__folder_actions)

        self._setup_docks_toolbar()

    def __setup_connections(self) -> None:
        self.__search_dock.search.connect(lambda: tutorials_model.search(self.__search_dock))
        disks_model.disk_checked_changed.connect(lambda: tutorials_model.search(self.__search_dock, True))
        tags_model.search_changed.connect(lambda: tutorials_model.search(self.__search_dock, True))

        self.__tutorials_dock.selection_changed.connect(self.__on_tutorials_dock_selection_changed)
        self.__recent_files.triggered.connect(self.__load_config)
        self.__scan_dialog.finished.connect(self.__on_scan_dialog_finished)

        config.loaded.connect(self.__on_config_loaded)

        scan_worker = scan_controller.worker
        scan_worker.scan_started.connect(self.__on_scan_worker_scan_started)
        scan_worker.scan_finished.connect(self.__on_scan_worker_scan_finished)

        tutorials_model.summary_changed.connect(self.__on_tutorials_model_summary_changed)

    def __cleanup_controllers(self) -> None:
        scan_controller.cleanup()

    def __setup_dialogs(self) -> None:
        self.__scan_dialog: Optional[ScanDialog] = None
        self.__scan_dialog = ScanDialog(parent=self)
        self.__scan_dialog.set_scan_worker(scan_controller.worker)

    def __refresh_models(self) -> None:
        disks_model.refresh()
        tutorials_model.refresh()
        tags_model.refresh()
        self.__tags_dock.view.expandAll()
        self.__update_ui_with_current_folder()

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
        self.__refresh_models()

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

        self.__refresh_models()

    def __on_tutorials_dock_selection_changed(self, tutorials: List[int]) -> None:
        self.__selected_one_folder = (len(tutorials) == 1)
        self.__current_folder_id = tutorials[0] if self.__selected_one_folder else None
        self.__update_ui_with_current_folder()

    def __on_open_folder_triggered(self) -> None:
        folder: Optional[Folder] = self.__get_current_folder(self.__current_folder_id)
        if folder is not None:
            path = folder.path()
            if path.exists():
                QDesktopServices.openUrl(QUrl(f'file://{path}', QUrl.TolerantMode))

    def __on_open_tc_triggered(self) -> None:
        folder: Optional[Folder] = self.__get_current_folder(self.__current_folder_id)
        if folder is not None:
            path = folder.path()
            if path.exists():
                tc_path = path / 'info.tc'
                if not tc_path.exists():
                    tc_path.touch()
                QDesktopServices.openUrl(QUrl(f'file://{tc_path}', QUrl.TolerantMode))

    def __update_ui_with_current_folder(self) -> None:
        folder_id = self.__current_folder_id
        folder = self.__get_current_folder(folder_id)
        online = (folder is not None and folder.disk.online)

        self.__info_tc_dock.set_folder(folder_id)
        self.__update_cover_dock(folder_id)
        self.__update_file_browser_dock(folder_id)
        selected_one_folder = (folder_id is not None)
        self.__open_folder_action.setEnabled(selected_one_folder and online)
        self.__open_tc_action.setEnabled(selected_one_folder and online)

    def __get_current_folder(self, folder_id: Optional[int]) -> Optional[Folder]:
        session = dal.session
        if session is not None and folder_id is not None:
            return session.query(Folder).filter(Folder.id_ == folder_id).first()
        return None

    def __update_file_browser_dock(self, folder_id: Optional[int]) -> None:
        path: Optional[Path] = None
        offline = False
        folder: Optional[Folder] = self.__get_current_folder(folder_id)
        if folder is not None:
            disk: Disk = folder.disk
            offline = not disk.online
            path = folder.path()

        self.__file_browser_dock.set_path(path)
        self.__file_browser_dock.set_offline(offline and path is not None)

    def __update_cover_dock(self, folder_id: Optional[int]) -> None:
        session = dal.session
        pixmap: Optional[QPixmap] = None
        offline = False
        file_format: Cover.FileFormat = Cover.FileFormat.NONE
        if session is not None and folder_id is not None:
            cover = session.query(Cover).join(Folder, Folder.cover_id == Cover.id_).filter(Folder.id_ == folder_id).first()
            if cover is not None:
                if cover.data is not None:
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover.data)
                    file_format = Cover.FileFormat(cover.file_format)
                offline = not cover.folder.disk.online

        self.__cover_dock.set_cover(pixmap)
        self.__cover_dock.set_has_cover(pixmap is not None or folder_id is None)
        self.__cover_dock.set_cover_format(file_format)
        self.__cover_dock.set_offline(offline and folder_id is not None)

    def show(self) -> None:
        super().show()
        self.__load_config(self.__recent_files.most_recent_file)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.__cleanup_controllers()
        super().closeEvent(event)

    def __on_tags_dock_view_activated(self, index: QModelIndex) -> None:
        tags_model.cycle_search_flag(index)

    def __on_tutorials_model_summary_changed(self, summary: str) -> None:
        self.__tutorials_summary.setText(summary)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
