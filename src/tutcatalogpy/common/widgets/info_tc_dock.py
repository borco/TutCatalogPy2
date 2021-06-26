import logging
from typing import Final, Optional

from PySide2.QtCore import QMargins, Qt
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QWidget
from PySide2.QtSvg import QSvgWidget

from tutcatalogpy.common.db.dal import dal
from tutcatalogpy.common.db.folder import Folder
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

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
    SVG_ICON_SIZE: Final[int] = 20

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/info_tc.svg')
    _dock_status_tip: Final[str] = 'Toggle tutorial info dock'

    __folder_id: Optional[int] = None
    __folder: Optional[Folder] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QGridLayout()
        layout.setMargin(0)
        widget.setLayout(layout)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        layout.addLayout(info_layout, 0, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.__no_info_tc = QSvgWidget(self.NO_INFO_TC_SVG)
        self.__no_info_tc.setStatusTip(self.NO_INFO_TC_TIP)

        self.__offline = QSvgWidget(self.OFFLINE_SVG)
        self.__offline.setStatusTip(self.OFFLINE_TIP)

        icons = [self.__no_info_tc, self.__offline]
        for icon in icons:
            icon.setFixedSize(self.SVG_ICON_SIZE, self.SVG_ICON_SIZE)
            icon.setVisible(False)
            info_layout.addWidget(icon)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def set_folder(self, folder_id: Optional[int]) -> None:
        self.__folder_id = folder_id
        if self.__folder_id is None or dal.session is None:
            self.__folder = None
        else:
            self.__folder = dal.session.query(Folder).filter(Folder.id_ == folder_id).one()

        self.__update_status_icons()
        log.info('Show info.tc for folder: %s', folder_id)

    def __update_status_icons(self) -> None:
        if self.__folder is None:
            self.__no_info_tc.setVisible(False)
            self.__offline.setVisible(False)
        else:
            self.__no_info_tc.setVisible(self.__folder.tutorial.size is None)
            self.__offline.setVisible(not self.__folder.disk.online)

if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
