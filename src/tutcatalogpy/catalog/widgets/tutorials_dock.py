import logging
from typing import Final

from PySide2.QtCore import QByteArray, QItemSelection, QModelIndex, QSettings, Qt, Signal
from PySide2.QtWidgets import QAction, QMenu, QTableView

from tutcatalogpy.catalog.models.tutorials_model import TutorialsModel
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TutorialsDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'tutorial_list_dock'
    SETTINGS_HEADER_STATE: Final[str] = 'header_state'
    SETTINGS_VERTICAL_HEADER_VISIBLE: Final[str] = 'vertical_header_visible'

    DOCK_TITLE: Final[str] = 'Tutorials'
    DOCK_OBJECT_NAME: Final[str] = 'tutorial_list_dock'

    TUTORIALS_VIEW_OBJECT_NAME: Final[str] = 'tutorials_view'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/tutorials.svg')
    _dock_status_tip: Final[str] = 'Toggle tutorials dock'

    selection_changed = Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        self.__tutorials_view = QTableView()
        self.__tutorials_view.setObjectName(self.TUTORIALS_VIEW_OBJECT_NAME)
        self.__tutorials_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__tutorials_view.setSortingEnabled(True)

        self.__tutorials_view.verticalHeader().setVisible(True)

        horizontal_header = self.__tutorials_view.horizontalHeader()
        horizontal_header.setSectionsMovable(True)
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSortIndicatorShown(True)
        horizontal_header.setContextMenuPolicy(Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(self.__on_header_custom_context_menu_requested)

        self.setWidget(self.__tutorials_view)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def __setup_context_menu(self) -> None:
        header = self.__tutorials_view.horizontalHeader()
        menu = QMenu(self)

        # vertical header
        label = 'Row Number'
        action = QAction(label, menu)
        action.setData(None)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(self.__on_header_custom_context_menu_triggered)
        menu.addAction(action)
        self.__vertical_header_visible_action = action

        # other columns
        for section in range(len(TutorialsModel.Columns)):
            label = TutorialsModel.Columns(section).label
            action = QAction(label, menu)
            action.setData(section)
            action.setCheckable(True)
            action.setChecked(not header.isSectionHidden(section))
            action.triggered.connect(self.__on_header_custom_context_menu_triggered)
            menu.addAction(action)
        self.__context_menu = menu

    def set_model(self, model) -> None:
        self.__tutorials_view.setModel(model)
        self.__tutorials_view.selectionModel().selectionChanged.connect(self.__on_tutorials_view_selection_changed)

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_HEADER_STATE, self.__tutorials_view.horizontalHeader().saveState())
        settings.setValue(self.SETTINGS_VERTICAL_HEADER_VISIBLE, self.__tutorials_view.verticalHeader().isVisible())
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        self.__tutorials_view.horizontalHeader().restoreState(QByteArray(settings.value(self.SETTINGS_HEADER_STATE, b'')))
        vertical_header_visible = settings.value(self.SETTINGS_VERTICAL_HEADER_VISIBLE, True, type=bool)
        settings.endGroup()

        self.__setup_context_menu()
        self.__tutorials_view.verticalHeader().setVisible(vertical_header_visible)
        self.__vertical_header_visible_action.setChecked(vertical_header_visible)

    def __on_header_custom_context_menu_requested(self, pos):
        self.__context_menu.exec_(self.__tutorials_view.mapToGlobal(pos))

    def __on_header_custom_context_menu_triggered(self, checked):
        if self.sender().data() is None:
            header = self.__tutorials_view.verticalHeader()
            header.setVisible(checked)
        else:
            header = self.__tutorials_view.horizontalHeader()
            header.setSectionHidden(self.sender().data(), not checked)

    def __on_tutorials_view_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        data_model: TutorialsModel = self.__tutorials_view.model()
        if data_model is None or type(data_model) is not TutorialsModel:
            return

        selection_model = self.__tutorials_view.selectionModel()

        folders = []
        index: QModelIndex
        for index in selection_model.selectedRows():
            folder = data_model.folder(index.row())
            folders.append(folder.id_)

        # log.info('Selected tutorials: %s', folders)

        self.selection_changed.emit(folders)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
