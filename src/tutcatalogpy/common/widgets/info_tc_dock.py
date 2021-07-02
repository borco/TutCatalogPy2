import logging
from typing import Final, Optional

from humanize import naturalsize
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QVBoxLayout, QScrollArea, QLabel, QWidget
from PySide2.QtSvg import QSvgWidget
from sqlalchemy.sql.schema import Table

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.db.tutorial import Tutorial
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.tutorial_data import TutorialData
from tutcatalogpy.common.widgets.dock_widget import DockWidget
from tutcatalogpy.common.widgets.elided_label import ElidedLabel
from tutcatalogpy.common.widgets.form_layout import FormLayout
from tutcatalogpy.common.widgets.path_view import PathView
from tutcatalogpy.common.widgets.tags_flow_widget import TagsFlowView

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class InfoTcDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'info_tc_dock'

    DOCK_TITLE: Final[str] = 'Tutorial Info'
    DOCK_OBJECT_NAME: Final[str] = 'info_tc_dock'  # used to identify this dock

    OFFLINE_SVG: Final[str] = relative_path(__file__, '../../resources/icons/offline.svg')
    OFFLINE_TIP: Final[str] = 'Offline'
    NO_INFO_TC_SVG: Final[str] = relative_path(__file__, '../../resources/icons/no_info_tc.svg')
    NO_INFO_TC_TIP: Final[str] = 'No info.tc'
    SVG_ICON_SIZE: Final[int] = 16

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/info_tc.svg')
    _dock_status_tip: Final[str] = 'Toggle tutorial info dock'

    __folder_id: Optional[int] = None
    __folder: Optional[Folder] = None

    tag_clicked = Signal(Table, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()
        self.__setup_connections()

    def __setup_widgets(self) -> None:
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.__scroll_area.setWidgetResizable(True)
        self.setWidget(self.__scroll_area)

        self.__widget = QWidget()
        self.__scroll_area.setWidget(self.__widget)

        layout = QVBoxLayout()
        self.__widget.setLayout(layout)

        self.__no_info_tc = QSvgWidget(self.NO_INFO_TC_SVG)
        self.__no_info_tc.setStatusTip(self.NO_INFO_TC_TIP)

        self.__offline = QSvgWidget(self.OFFLINE_SVG)
        self.__offline.setStatusTip(self.OFFLINE_TIP)

        icons = [self.__no_info_tc, self.__offline]
        for icon in icons:
            icon.setFixedSize(self.SVG_ICON_SIZE, self.SVG_ICON_SIZE)
            icon.setVisible(False)

        # main widgets
        form_layout = FormLayout()
        layout.addLayout(form_layout)

        self.__title = ElidedLabel()
        form_layout.add_horizontal_widgets('Title:', [self.__title, self.__no_info_tc, self.__offline])

        self.__authors = TagsFlowView()
        form_layout.addRow('Authors:', self.__authors)

        self.__released = QLabel()
        form_layout.addRow('Released:', self.__released)

        self.__level = QLabel()
        form_layout.addRow('Level:', self.__level)

        self.__duration = QLabel()
        form_layout.addRow('Duration:', self.__duration)

        self.__publisher = TagsFlowView()
        form_layout.addRow('Publisher:', self.__publisher)

        self.__path_name = PathView()
        form_layout.addRow('Folder Name:', self.__path_name)

        self.__path_parent = PathView()
        form_layout.addRow('Folder Parent:', self.__path_parent)

        self.__size = QLabel()
        form_layout.addRow('Size:', self.__size)

        layout.addStretch()

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def __setup_connections(self) -> None:
        for widget in [
            self.__publisher,
            self.__authors,
        ]:
            widget.tag_clicked.connect(self.tag_clicked.emit)

    def set_folder(self, folder_id: Optional[int]) -> None:
        self.__folder_id = folder_id
        if self.__folder_id is None or dal.session is None:
            self.__folder = None
        else:
            self.__folder = dal.session.query(Folder).filter(Folder.id_ == folder_id).one()

        self.__update_status_icons()
        self.__update_info()
        log.debug('Show info.tc for folder: %s', folder_id)

    def __update_status_icons(self) -> None:
        if self.__folder is None:
            self.__no_info_tc.setVisible(False)
            self.__offline.setVisible(False)
        else:
            self.__no_info_tc.setVisible(self.__folder.tutorial.size is None)
            self.__offline.setVisible(not self.__folder.disk.online)

    def __clear_form_widget(self) -> None:
        for widget in [
            self.__path_name,
            self.__path_parent,
            self.__size,
            self.__publisher,
            self.__title,
            self.__authors,
            self.__released,
            self.__duration,
            self.__level,
        ]:
            widget.clear()

    def __update_info(self) -> None:
        folder: Optional[Folder] = self.__folder
        if folder is None:
            self.__widget.setVisible(False)
            self.__clear_form_widget()
            return

        self.__widget.setVisible(True)

        path = folder.path()
        self.__path_name.set_path(path, folder.folder_name)

        path = path.parent
        self.__path_parent.set_path(path, path.name)

        self.__size.setText(naturalsize(self.__folder.size))

        tutorial: Tutorial = folder.tutorial

        self.__publisher.clear()
        self.__publisher.add_publisher(tutorial.publisher.name, tutorial.publisher_id)

        self.__title.setText(tutorial.title)

        author: Author
        self.__authors.clear()
        authors = list(tutorial.authors)
        authors.sort(key=lambda a: a.name.lower())
        for author in authors:
            self.__authors.add_author(author.name, author.id_)
        self.__authors.adjustSize()

        self.__released.setText(tutorial.released)

        self.__duration.setText(TutorialData.duration_to_text(tutorial.duration))

        self.__level.setText(TutorialData.level_to_text(tutorial.level))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
