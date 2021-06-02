import logging
from typing import Callable

from PySide2.QtCore import QObject, Signal


class LoggingHandler(logging.Handler):
    """Emits a Qt signal when something is logged."""

    class __Signaller(QObject):
        signal = Signal(str)

    def __init__(self, level = logging.DEBUG) -> None:
        super().__init__(level=level)
        self.__signaler = LoggingHandler.__Signaller()

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.__signaler.signal.emit(message)

    def connect(self, callback: Callable[[str], None]) -> None:
        self.__signaler.signal.connect(callback)
