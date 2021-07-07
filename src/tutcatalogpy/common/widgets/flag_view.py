from typing import Optional

from PySide2.QtWidgets import QLabel


class FlagView(QLabel):
    def __init__(self, highlight_if: Optional[bool] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__flag: Optional[bool] = None
        self.__update_text()
        self.__highlight_if = highlight_if

    def set_flag(self, value: Optional[bool]) -> None:
        self.__flag = value
        self.__update_text()

    def __update_text(self) -> None:
        if self.__flag is not None:
            text = 'yes' if self.__flag else 'no'
            if self.__flag == self.__highlight_if:
                text = '<font color="red">' + text + '</font>'
            self.setText(text)
        else:
            self.clear()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
