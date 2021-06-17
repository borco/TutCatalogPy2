import logging
from pathlib import Path
from typing import Final, Optional

from PySide2.QtCore import QByteArray, QSettings
from PySide2.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout, QWidget

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.models.file_browser_filter_proxy_model import FileBrowserFilterProxyModel
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FileBrowserDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'file_browser_dock'
    SETTINGS_HEADER_STATE: Final[str] = 'header_state'

    DOCK_TITLE: Final[str] = 'File Browser'
    DOCK_OBJECT_NAME: Final[str] = 'file_browser_dock'  # used to identify this dock

    _dock_icon = relative_path(__file__, '../../resources/icons/file_browser.svg')
    _dock_status_tip = 'Toggle file browser dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        self.__model: Optional[QFileSystemModel] = None
        self.__proxy: Optional[FileBrowserFilterProxyModel] = None

        self.__view = QTreeView()
        self.__view.setSortingEnabled(True)
        self.__view.setAlternatingRowColors(True)

        self.__header_state: Optional[QByteArray] = None

        self.setWidget(self.__view)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        header_state = self.__header_state if self.__header_state is not None else self.__view.header().saveState()
        settings.setValue(self.SETTINGS_HEADER_STATE, header_state)
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        self.__header_state = QByteArray(settings.value(self.SETTINGS_HEADER_STATE, b''))
        settings.endGroup()

    def set_path(self, path: Optional[Path]) -> None:
        if path is not None:
            if path.exists():
                old_proxy = self.__proxy
                old_model = self.__model

                header = self.__view.header()
                if self.__header_state is not None:
                    header_state = self.__header_state
                    self.__header_state = None
                else:
                    header_state = header.saveState()

                self.__view.setModel(None)

                p = str(path)

                self.__model = QFileSystemModel(self)
                self.__proxy = FileBrowserFilterProxyModel(self)
                self.__view.setModel(self.__proxy)

                self.__model.setRootPath(p)
                self.__proxy.setSourceModel(self.__model)
                self.__proxy.sort(header.sortIndicatorSection(), header.sortIndicatorOrder())
                self.__view.setRootIndex(self.__proxy.mapFromSource(self.__model.index(p)))

                header.restoreState(header_state)

                if old_proxy:
                    del old_proxy

                if old_model:
                    del old_model

                log.info('Showing folder %s', path)
                return

        if self.__model:
            self.__header_state = self.__view.header().saveState()
            self.__view.setModel(None)

            del self.__proxy
            self.__proxy = None

            del self.__model
            self.__model = None

        log.info('File browser cleared')


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
