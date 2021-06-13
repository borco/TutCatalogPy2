import logging
from typing import Final

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoverDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'cover_dock'

    DOCK_TITLE: Final[str] = 'Cover'
    DOCK_OBJECT_NAME: Final[str] = 'cover_dock'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/cover.svg')
    _dock_status_tip: Final[str] = 'Toggle cover dock'

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
