from PySide2.QtCore import QSettings
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QMainWindow


class CommonMainWindow(QMainWindow):
    SETTINGS_GROUP = 'main_window'
    SETTINGS_WINDOW_GEOMETRY = 'geometry'
    SETTINGS_WINDOW_STATE = 'state'

    def _save_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_WINDOW_GEOMETRY, self.saveGeometry())
        settings.setValue(self.SETTINGS_WINDOW_STATE, self.saveState())
        settings.endGroup()

    def _load_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        self.restoreGeometry(settings.value(self.SETTINGS_WINDOW_GEOMETRY, b''))
        self.restoreState(settings.value(self.SETTINGS_WINDOW_STATE, b''))
        settings.endGroup()

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        self._save_settings(settings)
        del settings
        super().closeEvent(event)

    def load_settings(self) -> None:
        settings = QSettings()
        self._load_settings(settings)
        del settings
