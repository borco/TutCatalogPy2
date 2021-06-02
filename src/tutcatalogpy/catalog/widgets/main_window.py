from typing import Final

from PySide2.QtWidgets import QFrame, QLabel

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.logging_dock import LoggingDock
from tutcatalogpy.common.widgets.main_window import CommonMainWindow


class MainWindow(CommonMainWindow):
    WINDOW_TITLE: Final[str] = 'TutCatalogPy2 Catalog'
    WINDOW_ICON_FILE: Final[str] = relative_path(__file__, '../../resources/icons/catalog.png')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.WINDOW_TITLE)

        self._setup_statusbar()
        self._setup_docks()
        self._setup_toolbars()

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


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
