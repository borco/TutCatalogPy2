import logging
from typing import Final

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class InfoTcDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'info_tc_dock'

    DOCK_TITLE: Final[str] = 'Tutorial Info'
    DOCK_OBJECT_NAME: Final[str] = 'info_tc_dock'  # used to identify this dock

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/info_tc.svg')
    _dock_status_tip: Final[str] = 'Toggle tutorial info dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        pass

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
