from abc import abstractmethod
from typing import Final, List, Optional

from PySide2.QtCore import QSettings, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QDockWidget, QLabel, QSizePolicy, QToolBar, QWidget

from tutcatalogpy.common.files import relative_path


class DockWidget(QDockWidget):
    DOCK_CLOSE_ICON: Final[str] = relative_path(__file__, '../../resources/icons/close.svg')
    DOCK_ICON_SIZE: Final[int] = 12
    DOCK_STYLESHEET: Final[str] = """
        QToolBar {background: #444; color: white;}
        QLabel {color: #444;}
    """

    _dock_icon: str
    _dock_status_tip: str

    toolbar_actions: List[QAction] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def setup_dock(self) -> None:
        action = self.toggleViewAction()
        action.setIcon(QIcon(self._dock_icon))
        action.setStatusTip(self._dock_status_tip)
        self.toolbar_actions.append(action)

    def _setup_dock_toolbar(self, actions: List[Optional[QAction]] = None) -> None:
        toolbar = QToolBar()
        # toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet(self.DOCK_STYLESHEET)
        toolbar.setIconSize(QSize(self.DOCK_ICON_SIZE, self.DOCK_ICON_SIZE))

        label = QLabel(f'  {self.windowTitle()}')
        toolbar.addWidget(label)

        if actions is not None:
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
        action.setIcon(QIcon(self.DOCK_CLOSE_ICON))
        action.triggered.connect(lambda: self.close())
        toolbar.addAction(action)

        self.setTitleBarWidget(toolbar)

    @abstractmethod
    def save_settings(self, settings: QSettings):
        pass

    @abstractmethod
    def load_settings(self, settings: QSettings):
        pass


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
