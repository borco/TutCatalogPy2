from typing import Final

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.logging_dock import LoggingDock
from tutcatalogpy.common.widgets.main_window import CommonMainWindow


class MainWindow(CommonMainWindow):
    WINDOW_TITLE: Final[str] = 'TutCatalogPy2 Viewer'
    WINDOW_ICON_FILE: Final[str] = relative_path(__file__, '../../resources/icons/viewer.png')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.WINDOW_TITLE)

        self._setup_statusbar()
        self._setup_docks()
        self._setup_docks_toolbar()

    def _setup_docks(self) -> None:
        self.__log_dock = LoggingDock()

        self._docks = [
            self.__log_dock,
        ]

        super()._setup_docks()


if __name__ == '__main__':
    from tutcatalogpy.viewer.main import run
    run()
