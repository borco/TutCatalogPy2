from typing import Optional
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLabel, QLayoutItem, QWidget
from sqlalchemy.sql.schema import Table

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.publisher import Publisher
from tutcatalogpy.common.widgets.flow_layout import FlowLayout


class TagItem(QLabel):
    clicked = Signal(Table, int)

    def __init__(self, text: str, table: Optional[Table] = None, index: Optional[int] = None):
        super().__init__()
        if table is not None and index is not None:
            text = '<a href="tag">' + text + '</a>'
        self.setText(text)
        self.__table: Optional[Table] = table
        self.__index: Optional[int] = index
        self.linkActivated.connect(lambda: self.clicked.emit(self.__table, self.__index))

    def same_with(self, item: Optional[QLayoutItem]) -> bool:
        return item is not None and item is TagItem and self.__table == item.__table and self.__index == item.__index


class TextItem(TagItem):
    def __init__(self, text: str):
        super().__init__(text)


class AuthorItem(TagItem):
    def __init__(self, text: str, index: int):
        super().__init__(text, table=Author, index=index)


class PublisherItem(TagItem):
    def __init__(self, text: str, index: int):
        super().__init__(text, table=Publisher, index=index)


class TagsWidget(QWidget):
    tag_clicked = Signal(Table, int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__layout = FlowLayout(margin=0)
        self.setLayout(self.__layout)

    def clear(self) -> None:
        self.__layout.clear()

    def add_text(self, text: str) -> None:
        self.__add_tag(TextItem(text))

    def add_author(self, text: str, index: int) -> None:
        self.__add_tag(AuthorItem(text, index))

    def add_publisher(self, text: str, index: int) -> None:
        self.__add_tag(PublisherItem(text, index))

    def __index_of(self, item: TagItem) -> Optional[int]:
        return next((index for index in range(self.__layout.count()) if item.same_with(self.__layout.itemAt(index))), None)

    def __add_tag(self, item: TagItem) -> None:
        index = self.__index_of(item)
        if index is not None:
            self.__layout.itemAt(index).setText(item.text())
        else:
            self.__layout.addWidget(item)
            item.clicked.connect(self.tag_clicked.emit)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QVBoxLayout

    app = QApplication([])
    window = QWidget(None)

    layout = QVBoxLayout()
    window.setLayout(layout)

    tags = TagsWidget()
    layout.addWidget(tags)

    tags.tag_clicked.connect(lambda table, tag: print(table, tag))
    tags.add_text('xxx:')
    tags.add_author('xxx 1', index=1)
    tags.add_author('xxx 2', index=2)
    tags.add_text('yyy:')
    tags.add_publisher('yyy 1', index=1)
    tags.add_publisher('yyy 2', index=2)

    window.resize(100, 100)
    window.show()

    app.exec_()
