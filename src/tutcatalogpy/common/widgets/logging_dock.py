from typing import Final

from PySide2.QtCore import QSettings
from PySide2.QtGui import QIcon, QTextOption
from PySide2.QtWidgets import QAction, QVBoxLayout, QWidget

import tutcatalogpy.common.logging_config as logging_config
from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.dock_widget import DockWidget
from tutcatalogpy.common.widgets.logging_browser import LoggingBrowser


class LoggingDock(DockWidget):
    SETTINGS_GROUP: Final[str] = 'log_dock'
    SETTINGS_LOG_SQL: Final[str] = 'log_sql'
    SETTINGS_LOG_DEBUG: Final[str] = 'log_debug'
    SETTINGS_LOG_VERBOSE: Final[str] = 'log_verbose'
    SETTINGS_LOG_WRAP: Final[str] = 'log_wrap'

    dock_title: Final[str] = 'Log'
    dock_object_name: Final[str] = 'log_dock'  # used to identify this dock
    dock_icon = relative_path(__file__, '../../resources/icons/log.svg')
    dock_status_tip = 'Toggle log dock'

    clear_icon: Final[str] = relative_path(__file__, '../../resources/icons/clear.svg')
    clear_tip: Final[str] = 'Clear logs.'
    toggle_debug_text: Final[str] = 'Debug'
    toggle_debug_tip: Final[str] = 'Toggle debug logging.'
    toggle_sql_text: Final[str] = 'SQL'
    toggle_sql_tip: Final[str] = 'Toggle SQL logging.'
    toggle_verbose_text: Final[str] = 'Verbose'
    toggle_verbose_tip: Final[str] = 'Toggle verbose logging.'
    toggle_wrap_icon: Final[str] = relative_path(__file__, '../../resources/icons/wrap_line.svg')
    toggle_wrap_tip: Final[str] = 'Wrap log lines.'

    show_sql: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.dock_title)
        self.setObjectName(self.dock_object_name)

        self.__setup_widgets()
        self.__setup_actions()

    def __setup_widgets(self) -> None:
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.__logging_browser = LoggingBrowser()
        layout.addWidget(self.__logging_browser)
        self.__logging_browser.setup(logging_config.gui_handler)

    def __setup_actions(self) -> None:
        self.__toggle_verbose = QAction()
        self.__toggle_verbose.setText(self.toggle_verbose_text)
        self.__toggle_verbose.setStatusTip(self.toggle_verbose_tip)
        self.__toggle_verbose.setCheckable(True)
        self.__toggle_verbose.setChecked(False)
        self.__toggle_verbose.triggered.connect(logging_config.toggle_verbose)

        self.__toggle_debug = QAction()
        self.__toggle_debug.setText(self.toggle_debug_text)
        self.__toggle_debug.setStatusTip(self.toggle_debug_tip)
        self.__toggle_debug.setCheckable(True)
        self.__toggle_debug.setChecked(False)
        self.__toggle_debug.triggered.connect(logging_config.toggle_debug)

        self.__toggle_sql = QAction()
        self.__toggle_sql.setText(self.toggle_sql_text)
        self.__toggle_sql.setStatusTip(self.toggle_sql_tip)
        self.__toggle_sql.setCheckable(True)
        self.__toggle_sql.setChecked(False)
        self.__toggle_sql.triggered.connect(logging_config.toggle_sql)
        self.__toggle_sql.setVisible(self.show_sql)

        self.__toggle_wrap = QAction()
        self.__toggle_wrap.setIcon(QIcon(self.toggle_wrap_icon))
        self.__toggle_wrap.setStatusTip(self.toggle_wrap_tip)
        self.__toggle_wrap.setCheckable(True)
        self.__toggle_wrap.setChecked(False)
        self.__toggle_wrap.toggled.connect(self.__on_wrap_toggled)

        self.__clear = QAction()
        self.__clear.setIcon(QIcon(self.clear_icon))
        self.__clear.setStatusTip(self.clear_tip)
        self.__clear.triggered.connect(self.__logging_browser.clear)

        self.setup_dock_toolbar([
            self.__toggle_verbose,
            self.__toggle_debug,
            self.__toggle_sql,
            self.__toggle_wrap,
            None,
            self.__clear,
        ])

        self.__on_wrap_toggled(self.__toggle_wrap.isChecked())

    def save_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.SETTINGS_LOG_DEBUG, self.__toggle_debug.isChecked())
        settings.setValue(self.SETTINGS_LOG_VERBOSE, self.__toggle_verbose.isChecked())
        settings.setValue(self.SETTINGS_LOG_SQL, self.__toggle_sql.isChecked())
        settings.setValue(self.SETTINGS_LOG_WRAP, self.__toggle_wrap.isChecked())
        settings.endGroup()

    def load_settings(self, settings: QSettings):
        settings.beginGroup(self.SETTINGS_GROUP)

        self.__toggle_debug.setChecked(settings.value(self.SETTINGS_LOG_DEBUG, False, type=bool))
        logging_config.toggle_debug(self.__toggle_debug.isChecked())

        if self.show_sql:
            self.__toggle_sql.setChecked(settings.value(self.SETTINGS_LOG_SQL, False, type=bool))
            logging_config.toggle_sql(self.__toggle_sql.isChecked())

        self.__toggle_verbose.setChecked(settings.value(self.SETTINGS_LOG_VERBOSE, False, type=bool))
        logging_config.toggle_verbose(self.__toggle_verbose.isChecked())

        self.__toggle_wrap.setChecked(settings.value(self.SETTINGS_LOG_WRAP, False, type=bool))

        settings.endGroup()

    def __on_wrap_toggled(self, checked: bool) -> None:
        self.__logging_browser.setWordWrapMode(QTextOption.WordWrap if checked else QTextOption.NoWrap)


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()