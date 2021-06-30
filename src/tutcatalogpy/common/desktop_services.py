import platform
from pathlib import Path

from PySide2.QtCore import QDir, QProcess, QUrl
from PySide2.QtGui import QDesktopServices


def open_path(path: Path, in_parent: bool = False) -> None:
    if path.exists():
        if in_parent:
            # https://stackoverflow.com/questions/3490336/how-to-reveal-in-finder-or-show-in-explorer-with-qt
            if platform.system() == 'Darwin':
                QProcess.execute('/usr/bin/osascript', [
                    '-e',
                    'tell application "Finder"',
                    '-e',
                    'activate',
                    '-e',
                    f'select POSIX file "{path.absolute()}"',
                    '-e',
                    'end tell',
                    '-e',
                    'return',
                ])
                return
            elif platform.system() == 'Windows':
                # NOT TESTED
                QProcess.startDetached('explorer.exe', ('/select,', QDir.toNativeSeparators(p)))
                return
            else:
                # don't know how to select this in parent
                # just open the parent
                p = path.parent
        else:
            p = path

        QDesktopServices.openUrl(QUrl(f'file://{p}', QUrl.TolerantMode))


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
