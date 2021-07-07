from typing import Any, List

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFormLayout, QHBoxLayout, QLayout, QVBoxLayout


class FormLayout(QFormLayout):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setLabelAlignment(Qt.AlignLeft)
        # self.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    def __add_widgets_to_layout(self, layout: QLayout, widgets: List[Any]) -> None:
        for w in widgets:
            if w is not None:
                layout.addWidget(w)
            else:
                layout.addStretch()

    def add_horizontal_widgets(self, text: str, widgets: List[Any]) -> None:
        layout = QHBoxLayout()
        self.__add_widgets_to_layout(layout, widgets)
        self.addRow(text, layout)

    def add_vertical_widgets(self, text: str, widgets: List[Any]) -> None:
        layout = QVBoxLayout()
        self.__add_widgets_to_layout(layout, widgets)
        self.addRow(text, layout)
