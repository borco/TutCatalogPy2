from pathlib import Path
from typing import Optional

from tutcatalogpy.common.desktop_services import open_path
from tutcatalogpy.common.widgets.elided_label import ElidedLabel


class PathView(ElidedLabel):
    def __init__(self, *args, **kwargs) -> None:
        self.__path: Path = Path()
        self.__text: Optional[str] = None
        self.__interactive: bool = False
        super().__init__(*args, **kwargs)
        self.triggered.connect(self.__on_triggered)

    def interactive(self) -> bool:
        return self.__interactive

    def setInteractive(self, value: bool) -> None:
        self.__interactive = value
        self.__update_ui()

    def set_path(self, path: Path, text: Optional[str] = None) -> None:
        self.__path = path
        self.__text = text if text is not None else str(path)
        self.setText(self.__text)
        self.setData(str(self.__path))
        self.__update_ui()

    def __update_ui(self) -> None:
        super().setInteractive(self.__interactive and self.__path.exists())
        self.setStatusTip(str(self.__path))

    def __on_triggered(self, text: str) -> None:
        if self.__path.exists():
            open_path(self.__path)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
