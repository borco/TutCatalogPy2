import logging
from typing import Final

from PySide2.QtCore import QSettings, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget
from tutcatalogpy.common.widgets.tags_flow_widget import TagsFlowView

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SearchDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'search_dock'
    SETTINGS_SEARCH_TEXT: Final[str] = 'search_text'
    SETTINGS_ONLY_SHOW_CHECKED_DISKS: Final[str] = 'only_show_checked_disks'

    DOCK_TITLE: Final[str] = 'Search'
    DOCK_OBJECT_NAME: Final[str] = 'search_dock'

    SEARCH_ICON: Final[str] = relative_path(__file__, '../../resources/icons/search.svg')

    ONLY_SHOW_CHECKED_DISKS_TEXT: Final[str] = 'Only show folders from checked disks'

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/search.svg')
    _dock_status_tip: Final[str] = 'Toggle search dock'

    search = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    @property
    def text(self) -> str:
        return self.__search_edit.text()

    @property
    def only_show_checked_disks(self) -> bool:
        return self.__only_show_checked_disks.isChecked()

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)
        search_layout.setMargin(0)

        self.__search_edit = QLineEdit()
        search_layout.addWidget(self.__search_edit)
        self.__search_edit.setClearButtonEnabled(True)
        self.__search_edit.editingFinished.connect(self.search)
        self.__search_edit.textChanged.connect(self.__on_search_edit_text_changed)

        self.__search_button = QToolButton()
        search_layout.addWidget(self.__search_button)
        self.__search_button.setIcon(QIcon(self.SEARCH_ICON))
        self.__search_button.clicked.connect(self.search)

        self.__only_show_checked_disks = QCheckBox(self.ONLY_SHOW_CHECKED_DISKS_TEXT)
        layout.addWidget(self.__only_show_checked_disks)
        self.__only_show_checked_disks.toggled.connect(self.search)

        self.__search_tags = TagsFlowView()
        layout.addWidget(self.__search_tags)

        layout.addStretch(1)

        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        widget.setSizePolicy(policy)

    @property
    def search_tags(self) -> TagsFlowView:
        return self.__search_tags

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def __on_search_edit_text_changed(self) -> None:
        if len(self.text) == 0:
            self.search.emit()

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_SEARCH_TEXT, self.__search_edit.text())
        settings.setValue(self.SETTINGS_ONLY_SHOW_CHECKED_DISKS, self.__only_show_checked_disks.isChecked())
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        self.__search_edit.setText(settings.value(self.SETTINGS_SEARCH_TEXT, ''))
        self.__only_show_checked_disks.setChecked(settings.value(self.SETTINGS_ONLY_SHOW_CHECKED_DISKS, False, type=bool))
        settings.endGroup()
        self.search.emit()

    def clear(self):
        self.__only_show_checked_disks.setChecked(False)
        self.__search_edit.clear()
        self.__search_tags.clear()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
