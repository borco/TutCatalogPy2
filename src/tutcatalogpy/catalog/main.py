import logging
import sys

from PySide2.QtWidgets import QApplication

from tutcatalogpy.catalog.widgets.main_window import MainWindow
from tutcatalogpy.common.settings import setup_settings
from tutcatalogpy.common.widgets.application import Application

log = logging.getLogger(__name__)
log.info('Launching app.')


def run():
    setup_settings('tutcatalogpy2-catalog')

    # can't extend QApplication because of a bug in Qt
    # that will result in a SIGSEGV when the garbage
    # collector runs at exit...
    Application.set_title(MainWindow.WINDOW_TITLE)
    app = QApplication(sys.argv)
    Application.set_icon(app, MainWindow.WINDOW_ICON_FILE)

    window = MainWindow()
    window.read_settings()
    window.show()

    success = app.exec_()
    sys.exit(success)


if __name__ == '__main__':
    run()
