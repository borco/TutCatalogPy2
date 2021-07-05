import logging
from pathlib import Path

from PySide2.QtCore import QCoreApplication, QSettings

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def setup_settings(path: str, name: str) -> None:
    QCoreApplication.setOrganizationName('Ioan Calin')
    QCoreApplication.setOrganizationDomain('borco.ro')
    QCoreApplication.setApplicationName(name)
    QSettings.setDefaultFormat(QSettings.IniFormat)

    # hack to allow each app version its own settings
    # if the application path contains 'devel' in it
    if 'devel' in path.lower():
        app_dir = str(Path(path).resolve().parent)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, app_dir)
    settings = QSettings()
    log.info('Using config file: %s', settings.fileName())
    del settings
