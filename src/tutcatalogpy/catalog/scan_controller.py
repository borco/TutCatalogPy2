from typing import List, Tuple

from PySide2.QtCore import QObject, QThread, Signal

from tutcatalogpy.catalog.scan_config import ScanConfig
from tutcatalogpy.catalog.scan_worker import ScanWorker


class ScanController(QObject):
    __scan = Signal(ScanConfig.Mode)
    __update_folder_details = Signal(list)

    def __init__(self) -> None:
        super().__init__()

        self.__worker_thread = QThread()
        self.__worker = ScanWorker()
        self.__worker.moveToThread(self.__worker_thread)
        self.__scan.connect(self.__worker.scan)
        self.__update_folder_details.connect(self.__worker.update_folder_details)

    def scan_startup(self) -> None:
        self.__scan.emit(ScanConfig.Mode.STARTUP)

    def scan_normal(self) -> None:
        self.__scan.emit(ScanConfig.Mode.NORMAL)

    def scan_extended(self) -> None:
        self.__scan.emit(ScanConfig.Mode.EXTENDED)

    def update_folder_details(self, folders: List[Tuple[str, str, str]]) -> None:
        self.__update_folder_details.emit(folders)

    def setup(self) -> None:
        self.__worker_thread.start()

    def cleanup(self) -> None:
        self.__worker.cancel()
        self.__worker_thread.quit()
        self.__worker_thread.wait()

    @property
    def worker(self) -> ScanWorker:
        return self.__worker


scan_controller = ScanController()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
