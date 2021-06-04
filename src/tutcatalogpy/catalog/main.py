import logging
import sys

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QApplication

import tutcatalogpy.common.logging_config  # noqa: F401
from tutcatalogpy.catalog.scan_config import scan_config
from tutcatalogpy.catalog.widgets.main_window import MainWindow
from tutcatalogpy.common.settings import setup_settings
from tutcatalogpy.common.widgets.application import Application

log = logging.getLogger(__name__)
log.info('Launching app.')


def load_settings():
    setup_settings('tutcatalogpy2-catalog')
    settings = QSettings()
    scan_config.load_settings(settings)
    del settings


def save_settings():
    settings = QSettings()
    scan_config.save_settings(settings)
    del settings


def run():
    load_settings()

    # can't extend QApplication because of a bug in Qt
    # that will result in a SIGSEGV when the garbage
    # collector runs at exit...
    # https://bugreports.qt.io/browse/PYSIDE-1447
    Application.set_title(MainWindow.WINDOW_TITLE)
    app = QApplication(sys.argv)
    Application.set_icon(app, MainWindow.WINDOW_ICON_FILE)

    window = MainWindow()
    window.load_settings()
    window.show()

    success = app.exec_()
    save_settings()
    sys.exit(success)


if __name__ == '__main__':
    run()
