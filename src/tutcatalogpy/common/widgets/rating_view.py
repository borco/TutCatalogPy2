from typing import Final

from PySide2.QtCore import QRectF
from PySide2.QtGui import QPainter, QPaintEvent
from PySide2.QtSvg import QSvgRenderer
from PySide2.QtWidgets import QWidget

from tutcatalogpy.common.files import relative_path


class RatingView(QWidget):
    MINIMUM: Final[int] = -5
    MAXIMUM: Final[int] = 5

    good_star: Final[str] = relative_path(__file__, '../../resources/icons/good_star.svg')
    bad_star: Final[str] = relative_path(__file__, '../../resources/icons/bad_star.svg')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__rating = 0
        self.setMinimumSize(1, 1)  # force a paint event

    def set_rating(self, value: int) -> None:
        value = min(self.MAXIMUM, max(self.MINIMUM, value))
        if self.__rating == value:
            return
        self.__rating = value
        self.update()

    def clear(self) -> None:
        self.set_rating(0)

    def paintEvent(self, event: QPaintEvent) -> None:
        value = self.__rating
        if value < 0:
            value = abs(value)
            svg_file = self.bad_star
        else:
            svg_file = self.good_star

        painter = QPainter(self)

        metrics = painter.fontMetrics()
        size = metrics.boundingRect('X').height()
        min_height = size
        min_width = size * max(abs(self.MAXIMUM), abs(self.MINIMUM))
        self.setMinimumSize(min_width, min_height)

        renderer = QSvgRenderer(svg_file)

        for index in range(value):
            rect = QRectF(index * size, 0, size, size)
            renderer.render(painter, rect)

        painter.end()


if __name__ == '__main__':
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication, QSlider, QVBoxLayout

    app = QApplication([])
    window = QWidget(None)

    layout = QVBoxLayout()
    window.setLayout(layout)

    for value in range(-6, 6):
        rating = RatingView(window)
        rating.set_rating(value)
        layout.addWidget(rating)

    rating = RatingView(window)
    layout.addWidget(rating)

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(RatingView.MINIMUM)
    slider.setMaximum(RatingView.MAXIMUM)
    slider.setValue(0)
    layout.addWidget(slider)

    slider.valueChanged.connect(rating.set_rating)

    layout.addStretch()

    window.setMinimumWidth(300)
    window.show()

    app.exec_()
