from dataclasses import dataclass
from typing import Dict, Optional

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLabel


@dataclass
class TagsWidgetItem:
    text: str = ''
    table: Optional['Table'] = None
    index: Optional[int] = None
    interactive: bool = True


class TagsWidget(QLabel):
    triggered = Signal(TagsWidgetItem)

    __tags: Dict[str, TagsWidgetItem] = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.linkActivated.connect(self.__on_link_activated)

    def clear(self) -> None:
        self.__tags.clear()
        self.setText('')

    def add_tag(self, key: str, tag: TagsWidgetItem) -> None:
        self.__tags[key] = tag
        prev_interactive = False
        text = ''
        for k, v in self.__tags.items():
            if prev_interactive:
                text += ', ' if v.interactive else ' '
            prev_interactive = v.interactive
            text += f'<a href="{k}">{v.text}</a>' if v.interactive else (v.text + ' ')
        self.setText(text)

    def __on_link_activated(self, key: str) -> None:
        self.triggered.emit(self.__tags[key])


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QWidget

    app = QApplication([])
    window = QWidget(None)

    tags = TagsWidget(window)
    tags.setWordWrap(True)
    tags.triggered.connect(lambda tag: print(tag))
    tags.add_tag('xxx:', TagsWidgetItem('xxx:', interactive=False))
    tags.add_tag('xxx:xxx 1', TagsWidgetItem('xxx 1', index=1))
    tags.add_tag('xxx:xxx 2', TagsWidgetItem('xxx 2', index=2))
    tags.add_tag('yyy:', TagsWidgetItem('yyy:', interactive=False))
    tags.add_tag('yyy:yyy 1', TagsWidgetItem('yyy 1', index=1))
    tags.add_tag('yyy:yyy 2', TagsWidgetItem('yyy 2', index=2))

    window.resize(100, 100)
    window.show()

    app.exec_()
