import sys
from typing import Optional

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication


class Application(QApplication):

    @staticmethod
    def set_title(title: Optional[str]) -> None:
        if title is None:
            return

        if sys.platform.startswith('darwin'):
            try:
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                if bundle is not None:
                    app_info = (
                        bundle.localizedInfoDictionary() or bundle.infoDictionary()
                    )
                    if app_info is not None:
                        app_info['CFBundleName'] = title
            except Exception as err:
                print(err)

    @staticmethod
    def set_icon(application: QApplication, icon_file: Optional[str]) -> None:
        if icon_file is None or icon_file == '':
            return

        icon = QIcon(icon_file)
        application.setWindowIcon(icon)
