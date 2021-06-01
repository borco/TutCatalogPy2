from PySide2.QtCore import QCoreApplication, QSettings


def setup_settings(name: str) -> None:
    QCoreApplication.setOrganizationName('Ioan Calin')
    QCoreApplication.setOrganizationDomain('borco.ro')
    QCoreApplication.setApplicationName(name)
    QSettings.setDefaultFormat(QSettings.IniFormat)
