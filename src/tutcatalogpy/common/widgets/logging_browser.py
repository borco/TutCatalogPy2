from typing import Final

from PySide2.QtGui import QTextDocument
from PySide2.QtWidgets import QTextEdit

from tutcatalogpy.common.logging_handler import LoggingHandler


class LoggingBrowser(QTextEdit):
    CSS: Final[str] = """
.header {
    font-size: small;
}

.source {
    font-size: small;
    color: #aaa;
}

.levelname {
    font-weight: bold;
}

td.levelname {
    font-weight: normal;
    color: #bbb;
}

.defaultname {
    color: #bbb;
}

.exception_info {
    color: #85144b;
    font-size: small;
}

.duration {
    color: red;
}

td.duration {
    text-align:right;
}

.DEBUG {
    background: #7FDBFF;
}

.INFO {
    background: #DDDDDD;
}

.WARNING {
    background: #FFDC00;
}

.ERROR {
    background: #FF4136;
    color: #FFF;
    float: left;
    width: 60px;
}

.CRITICAL {
    background: #85144b;
    color: #FFF;
}
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)

        self.__document = QTextDocument()
        self.__document.setDefaultStyleSheet(self.CSS)
        self.setDocument(self.__document)

    def setup(self, handler: LoggingHandler) -> None:
        handler.connect(self.__on_message_logged)

    def __on_message_logged(self, message: str) -> None:
        self.append(message)
        self.horizontalScrollBar().setValue(0)


if __name__ == '__main__':
    import logging
    from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
    from tutcatalogpy.common.logging_config import gui_handler

    app = QApplication([])

    window = QMainWindow()
    widget = QWidget()
    window.setCentralWidget(widget)

    layout = QVBoxLayout()
    widget.setLayout(layout)

    logging_browser = LoggingBrowser()
    logging_browser.setup(gui_handler)
    layout.addWidget(logging_browser)

    app_logger = logging.getLogger('app')

    app_logger.debug('debug')
    app_logger.info('info')
    app_logger.warning('warning')
    app_logger.error('error')
    app_logger.critical('critical')
    try:
        raise RuntimeError('test exception')
    except Exception:
        app_logger.exception('exception')
    app_logger.info('duration examples')
    app_logger.duration('1h 30m', 'xxx')
    app_logger.duration('1h 20m', 'yyy')

    window.resize(900, 600)
    window.show()
    app.exec_()
