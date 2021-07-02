from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QTextEdit


class GrowingTextEdit(QTextEdit):
    text_changed = Signal(str)

    def __init__(self, line_edit: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__line_edit = line_edit
        self.document().contentsChanged.connect(self.__on_contents_changed)
        self.document().documentLayout().documentSizeChanged.connect(self.__adjust_size)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.__min_height = 0
        self.__max_height = 65000

    def __on_contents_changed(self) -> None:
        self.__adjust_size()
        self.text_changed.emit(self.toPlainText())

    def __adjust_size(self):
        doc_height = self.document().size().height()
        if self.__min_height <= doc_height <= self.__max_height:
            margins = self.contentsMargins()
            height = int(doc_height + margins.top() + margins.bottom())
            if self.__line_edit:
                self.setFixedHeight(height)
            else:
                self.setMinimumHeight(height)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
