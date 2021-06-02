from typing import Final, List, Optional

from PySide2.QtCore import QSettings, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QDockWidget, QLabel, QSizePolicy, QToolBar, QWidget

from tutcatalogpy.common.files import relative_path


class DockWidget(QDockWidget):
    dock_icon: str
    dock_status_tip: str
    dock_icon_size: Final[int] = 12
    dock_stylesheet: Final[str] = """
        QToolBar {background: #444; color: white;}
        QLabel {color: #444;}
    """
    dock_close_icon: Final[str] = relative_path(__file__, '../../resources/icons/close.svg')
    toolbar_actions: List[QAction] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def setup_dock(self) -> None:
        action = self.toggleViewAction()
        action.setIcon(QIcon(self.dock_icon))
        action.setStatusTip(self.dock_status_tip)
        self.toolbar_actions.append(action)

    def setup_dock_toolbar(self, actions: List[Optional[QAction]]) -> None:
        toolbar = QToolBar()
        # toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet(self.dock_stylesheet)
        toolbar.setIconSize(QSize(self.dock_icon_size, self.dock_icon_size))

        label = QLabel(f'  {self.windowTitle()}')
        toolbar.addWidget(label)

        if len(actions) > 0:
            toolbar.addSeparator()

        for action in actions:
            if action is None:
                toolbar.addSeparator()
            else:
                toolbar.addAction(action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        action = QAction(self)
        action.setIcon(QIcon(self.dock_close_icon))
        action.triggered.connect(lambda: self.close())
        toolbar.addAction(action)

        self.setTitleBarWidget(toolbar)

    def save_settings(self, settings: QSettings):
        pass

    def load_settings(self, settings: QSettings):
        pass


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
