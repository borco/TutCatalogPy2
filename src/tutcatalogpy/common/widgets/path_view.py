from pathlib import Path
from typing import Optional

from tutcatalogpy.common.desktop_services import open_path
from tutcatalogpy.common.widgets.elided_label import ElidedLabel


class PathView(ElidedLabel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tip = ElidedLabel.Tip.SHOW_DATA
        self.__path: Path = Path()
        self.__text: Optional[str] = None
        self.triggered.connect(self.__on_triggered)

    def set_path(self, path: Path, text: Optional[str] = None) -> None:
        self.__path = path
        self.__text = text if text is not None else str(path)
        self.tip = ElidedLabel.Tip.SHOW_DATA
        self.set_text(self.__text)
        self.set_data(str(self.__path))

    def __on_triggered(self, text: str) -> None:
        if self.__path.exists():
            open_path(self.__path)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
