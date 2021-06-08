import logging
from typing import Final, List, Tuple

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QCheckBox, QGridLayout, QLabel, QVBoxLayout, QWidget

from tutcatalogpy.catalog.scan_config import ScanConfig, scan_config
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ScanConfigDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'scan_config_dock'

    DOCK_TITLE: Final[str] = 'Scan Config'
    DOCK_OBJECT_NAME: Final[str] = 'scan_config_dock'

    SCAN_ICONS: Final[List[Tuple[str, str]]] = [
        ('Startup scan', relative_path(__file__, '../../resources/icons/scan_startup.svg')),
        ('Normal scan', relative_path(__file__, '../../resources/icons/scan.svg')),
        ('Extended scan', relative_path(__file__, '../../resources/icons/scan_more.svg')),
    ]

    _dock_icon: Final[str] = relative_path(__file__, '../../resources/icons/scan_config.svg')
    _dock_status_tip: Final[str] = 'Toggle scan config dock'

    class CheckBox(QCheckBox):
        def __init__(self, mode: ScanConfig.Mode, option: ScanConfig.Option, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.mode = mode
            self.option = option

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.DOCK_TITLE)
        self.setObjectName(self.DOCK_OBJECT_NAME)

        self.__setup_widgets()
        self._setup_dock_toolbar()

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        grid = QGridLayout()
        layout.addLayout(grid)
        grid.setColumnStretch(0, 1)

        grid.addWidget(QLabel('<b>Options</b>'), 0, 0)

        for index, (status, path) in enumerate(self.SCAN_ICONS):
            label = QLabel()
            label.setPixmap(QPixmap(path))
            label.setStatusTip(status)
            grid.addWidget(label, 0, index + 1, Qt.AlignHCenter)

        for row_index, option in enumerate(ScanConfig.Option):
            if option == ScanConfig.Option.NOTHING:
                continue

            text = option.name.replace('_', ' ').capitalize()
            grid.addWidget(QLabel(text), row_index + 1, 0)

            for column_index, mode in enumerate([ScanConfig.Mode.STARTUP, ScanConfig.Mode.NORMAL, ScanConfig.Mode.EXTENDED]):
                checkbox = ScanConfigDock.CheckBox(mode, option)
                checkbox.setChecked(scan_config.option[mode] & option)
                checkbox.toggled.connect(self.__on_checkbox_toggled)
                grid.addWidget(checkbox, row_index + 1, column_index + 1, Qt.AlignHCenter)

        layout.addStretch()

    def __on_checkbox_toggled(self) -> None:
        checkbox: ScanConfigDock.CheckBox = self.sender()
        scan_config.option[checkbox.mode] ^= checkbox.option
        log.info('mode: %s set to %s', checkbox.mode, scan_config.option[checkbox.mode])


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
