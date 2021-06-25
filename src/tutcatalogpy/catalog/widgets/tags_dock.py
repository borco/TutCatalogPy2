import logging
from typing import Final, Optional

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QTreeView

from tutcatalogpy.catalog.models.tags_model import TagsModel
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TagsDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'tags_dock'

    DOCK_TITLE: Final[str] = 'Tags'
    DOCK_OBJECT_NAME: Final[str] = 'tags_dock'

    CLEAR_ICON: Final[str] = relative_path(__file__, '../../resources/icons/clear.svg')
    CLEAR_TIP: Final[str] = 'Clear tags used in search'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/tags.svg')
    _dock_status_tip: Final[str] = 'Toggle tags dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    @property
    def view(self) -> QTreeView:
        return self.__tags_view

    def __setup_widgets(self) -> None:
        self.__tags_view = QTreeView()
        self.setWidget(self.__tags_view)
        self.__tags_view.setHeaderHidden(True)

    def __setup_actions(self) -> None:
        self.__clear = QAction()
        self.__clear.setIcon(QIcon(self.CLEAR_ICON))
        self.__clear.setStatusTip(self.CLEAR_TIP)
        self.__clear.triggered.connect(self.__on_clear_triggered)

        self._setup_dock_toolbar([
            self.__clear
        ])

    def set_model(self, model: TagsModel) -> None:
        self.__tags_view.setModel(model)

    def __on_clear_triggered(self) -> None:
        model: Optional[TagsModel] = self.__tags_view.model()
        if model is not None:
            model.clear_search_flags()
            self.__tags_view.expandAll()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
