import logging
from typing import Final

from PySide2.QtCore import QSettings, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QToolButton, QVBoxLayout, QWidget

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TagsDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'tags_dock'

    DOCK_TITLE: Final[str] = 'Tags'
    DOCK_OBJECT_NAME: Final[str] = 'tags_dock'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/tags.svg')
    _dock_status_tip: Final[str] = 'Toggle tags dock'

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
