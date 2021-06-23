import logging
from typing import Final

from PySide2.QtWidgets import QTreeView

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
        self.__tags_view = QTreeView()
        self.setWidget(self.__tags_view)
        self.__tags_view.setHeaderHidden(True)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def set_model(self, model) -> None:
        self.__tags_view.setModel(model)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
