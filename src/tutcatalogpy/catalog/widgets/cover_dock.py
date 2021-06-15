import logging
from typing import Final, Optional

from PySide2.QtCore import QMargins, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget
from PySide2.QtSvg import QSvgWidget


from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.aspectratiopixmaplabel import AspectRatioPixmapLabel
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoverDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'cover_dock'

    DOCK_TITLE: Final[str] = 'Cover'
    DOCK_OBJECT_NAME: Final[str] = 'cover_dock'

    NO_COVER_SVG: Final[str] = relative_path(__file__, '../../resources/icons/no_cover.svg')
    NO_COVER_TIP: Final[str] = 'No cover'
    OFFLINE_SVG: Final[str] = relative_path(__file__, '../../resources/icons/offline.svg')
    OFFLINE_TIP: Final[str] = 'Offline'
    SVG_ICON_SIZE: Final[int] = 20

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/cover.svg')
    _dock_status_tip: Final[str] = 'Toggle cover dock'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self.__setup_actions()

        self.set_cover(None)
        self.set_online(False)

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QGridLayout()
        layout.setMargin(0)
        widget.setLayout(layout)

        self.__cover = AspectRatioPixmapLabel()

        layout.addWidget(self.__cover, 0, 0)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        layout.addLayout(info_layout, 0, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.__size_label = QLabel()
        info_layout.addWidget(self.__size_label)

        self.__no_cover = QSvgWidget(self.NO_COVER_SVG)
        self.__no_cover.setStatusTip(self.NO_COVER_TIP)

        self.__offline = QSvgWidget(self.OFFLINE_SVG)
        self.__offline.setStatusTip(self.OFFLINE_TIP)

        icons = [self.__no_cover, self.__offline]
        for icon in icons:
            icon.setFixedSize(self.SVG_ICON_SIZE, self.SVG_ICON_SIZE)
            icon.setVisible(False)
            info_layout.addWidget(icon)

    def __setup_actions(self) -> None:
        self._setup_dock_toolbar()

    def set_cover(self, pixmap: Optional[QPixmap]) -> None:
        self.__cover.setPixmap(pixmap)
        self.__no_cover.setVisible(pixmap is None)
        if pixmap is None:
            self.__size_label.setText('')
        else:
            self.__size_label.setText(f'{pixmap.width()} x {pixmap.height()}')

    def set_online(self, online: bool) -> None:
        self.__offline.setVisible(not online)


def run() -> None:
    from tutcatalogpy.catalog.main import run
    run()
    # import sys
    # from PySide2.QtWidgets import QApplication, QMainWindow

    # app = QApplication(sys.argv)

    # pixmap = QPixmap(relative_path(__file__, '../../resources/icons/cover.png'))
    # window = QMainWindow()
    # cover = CoverDock()
    # cover.set_cover(pixmap)
    # window.setCentralWidget(cover)
    # window.show()

    # success = app.exec_()
    # sys.exit(success)


if __name__ == '__main__':
    run()
