from PySide2.QtWidgets import QFrame


class HorizontalSeparator(QFrame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
