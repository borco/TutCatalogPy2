import enum
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import uuid4

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLabel
from sqlalchemy.sql.schema import Table

from tutcatalogpy.common.db.author import Author
from tutcatalogpy.common.db.publisher import Publisher


@dataclass
class TagsWidgetItem:
    class Type(bytes, enum.Enum):
        prefix: str
        table: Optional[Table]
        interactive: bool

        def __new__(cls, value: int, prefix: str, table: Optional[Table], interactive: bool = True):
            obj = bytes.__new__(cls, [value])
            obj._value_ = value
            obj.prefix = prefix
            obj.table = table
            obj.interactive = interactive
            return obj

        TEXT = (0, '', None, False)
        AUTHOR = (1, 'author:', Author)
        PUBLISHER = (2, 'publisher:', Publisher)

    text: str = ''
    type_: Type = Type.TEXT
    index: Optional[int] = None


class TagsWidget(QLabel):
    tag_clicked = Signal(Table, int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__tags: Dict[str, TagsWidgetItem] = {}
        self.linkActivated.connect(self.__on_link_activated)
        self.setWordWrap(True)

    def clear(self) -> None:
        self.setText('')
        self.__tags.clear()

    def add_text(self, text: str) -> None:
        self.__add_tag(TagsWidgetItem(text))

    def add_author(self, text: str, index: int) -> None:
        self.__add_tag(TagsWidgetItem(text, TagsWidgetItem.Type.AUTHOR, index))

    def add_publisher(self, text: str, index: int) -> None:
        self.__add_tag(TagsWidgetItem(text, TagsWidgetItem.Type.PUBLISHER, index))

    def __add_tag(self, tag: TagsWidgetItem) -> None:
        if tag.type_ == TagsWidgetItem.Type.TEXT:
            key = str(uuid4())
        else:
            key = tag.type_.prefix + str(tag.index)
        self.__tags[key] = tag

        prev_interactive = False
        text = ''
        for k, v in self.__tags.items():
            if prev_interactive:
                text += ', ' if v.type_.interactive else ' '
            text += f'<a href="{k}">{v.text}</a>' if v.type_.interactive else (v.text + ' ')
            prev_interactive = v.type_.interactive
        self.setText(text)

    def __on_link_activated(self, key: str) -> None:
        tag = self.__tags[key]
        self.tag_clicked.emit(tag.type_.table, tag.index)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication([])
    window = QWidget(None)

    layout = QVBoxLayout()
    window.setLayout(layout)

    tags = TagsWidget()
    layout.addWidget(tags)

    tags.setWordWrap(True)
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
