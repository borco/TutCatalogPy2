from typing import Optional

from PySide2.QtWidgets import QLabel


class FlagView(QLabel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__flag: Optional[bool] = None
        self.__update_text()

    def set_flag(self, value: Optional[bool]) -> None:
        self.__flag = value
        self.__update_text()

    def __update_text(self) -> None:
        if self.__flag is not None:
            self.setText('yes' if self.__flag else '<font color="red">no</font>')
        else:
            self.clear()
