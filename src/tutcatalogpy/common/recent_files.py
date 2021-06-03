from pathlib import Path
from typing import Dict, Final, Union

from PySide2.QtCore import QObject, QSettings, Signal
from PySide2.QtWidgets import QAction, QMenu, QWidget


class RecentFiles(QObject):
    SETTINGS_ARRAY: Final[str] = 'recent_files'
    FILE_SETTINGS_KEY: Final[str] = 'file'

    CLEAR_ACTION_TEXT: Final[str] = 'Clear Recently Opened'

    triggered = Signal(str)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__actions: Dict[str, QAction] = {}

        self.__clearAction: Final[QAction] = QAction(self.CLEAR_ACTION_TEXT, self)
        self.__clearAction.triggered.connect(self.clear)

        self.__menu: Final[QMenu] = QMenu('Open Recent')
        self.__menu.addSeparator()
        self.__menu.addAction(self.__clearAction)

        self.__menu.setEnabled(False)

    @property
    def menu(self) -> QMenu:
        return self.__menu

    def __most_recent_action(self) -> Union[QAction, None]:
        action = self.__menu.actions()[0]
        if action.isSeparator() is False:
            return action
        return None

    @property
    def most_recent_file(self) -> Union[str, None]:
        action = self.__most_recent_action()
        if action is not None:
            return action.data()
        return None

    def load_settings(self, settings: QSettings):
        size = settings.beginReadArray(self.SETTINGS_ARRAY)
        for index in range(size - 1, -1, -1):
            settings.setArrayIndex(index)
            self.add_file(settings.value(self.FILE_SETTINGS_KEY))
        settings.endArray()

    def save_settings(self, settings: QSettings):
        settings.beginWriteArray(self.SETTINGS_ARRAY)
        actions = self.__menu.actions()[:-2]
        for index in range(len(actions)):
            settings.setArrayIndex(index)
            action: QAction = actions[index]
            settings.setValue(self.FILE_SETTINGS_KEY, action.data())
        settings.endArray()

    def clear(self):
        for _, action in self.__actions.items():
            self.__menu.removeAction(action)
        self.__actions.clear()
        self.__menu.setEnabled(False)

    def add_file(self, file_name: str):
        action = self.__actions.pop(file_name, None)
        if action is not None:
            self.__menu.removeAction(action)

        action = QAction(self)
        action.setText(Path(file_name).name)
        action.setData(file_name)
        action.setStatusTip(f'Open config {file_name}')
        action.triggered.connect(lambda: self.triggered.emit(file_name))
        self.__actions[file_name] = action
        self.__menu.insertAction(self.__menu.actions()[0], action)
        self.__menu.setEnabled(True)
