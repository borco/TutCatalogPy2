from PySide2.QtCore import QSettings
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QMainWindow


class CommonMainWindow(QMainWindow):
    SETTINGS_GROUP = 'main_window'
    SETTINGS_WINDOW_GEOMETRY = 'geometry'
    SETTINGS_WINDOW_STATE = 'state'

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_WINDOW_GEOMETRY, self.saveGeometry())
        settings.setValue(self.SETTINGS_WINDOW_STATE, self.saveState())
        del settings
        super().closeEvent(event)

    def read_settings(self) -> None:
        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)
        self.restoreGeometry(settings.value(self.SETTINGS_WINDOW_GEOMETRY, b''))
        self.restoreState(settings.value(self.SETTINGS_WINDOW_STATE, b''))
        del settings
