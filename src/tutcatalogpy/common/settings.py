import logging

from PySide2.QtCore import QCoreApplication, QSettings

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def setup_settings(name: str) -> None:
    QCoreApplication.setOrganizationName('Ioan Calin')
    QCoreApplication.setOrganizationDomain('borco.ro')
    QCoreApplication.setApplicationName(name)
    QSettings.setDefaultFormat(QSettings.IniFormat)
    settings = QSettings()
    log.info('Using config file: %s', settings.fileName())
    del settings
