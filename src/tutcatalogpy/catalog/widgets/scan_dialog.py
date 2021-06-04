import logging
from typing import Final

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QProgressBar, QVBoxLayout

from tutcatalogpy.catalog.scan_worker import ScanWorker
from tutcatalogpy.common.widgets.elided_label import ElidedLabel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ScanDialog(QDialog):

    MAX_SCAN_TIME_SEC_TO_AUTOCLOSE: Final[int] = 10

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__scan_worker = None

        self.setWindowFlags(Qt.Sheet)

        layout = QVBoxLayout()

        grid = QGridLayout()
        layout.addLayout(grid)
        grid.setColumnStretch(1, 1)

        row = 0

        self.__step = QLabel()
        grid.addWidget(QLabel('Scanning:'), row, 0)
        grid.addWidget(self.__step, row, 1)
        row += 1

        self.__disk = QLabel()
        grid.addWidget(QLabel('Disk:'), row, 0)
        grid.addWidget(self.__disk, row, 1)
        row += 1

        self.__tutorial_path = ElidedLabel()
        grid.addWidget(QLabel('Path:'), row, 0)
        grid.addWidget(self.__tutorial_path, row, 1)
        row += 1

        self.__tutorial_name = ElidedLabel()
        grid.addWidget(QLabel('Name:'), row, 0)
        grid.addWidget(self.__tutorial_name, row, 1)
        row += 1

        self.__elapsed_time = QLabel()
        grid.addWidget(QLabel('Elapsed:'), row, 0)
        grid.addWidget(self.__elapsed_time, row, 1)
        row += 1

        self.__folder_progress = QProgressBar()
        self.__folder_progress.setEnabled(False)
        self.__folder_progress.setMaximum(0)
        self.__folder_progress.setValue(0)
        layout.addWidget(self.__folder_progress)

        layout.addStretch()

        button_box = QDialogButtonBox()
        layout.addWidget(button_box)

        self.__close_button = button_box.addButton('Cancel', QDialogButtonBox.AcceptRole)
        if self.__close_button is not None:
            self.__close_button.setDefault(True)
            self.__close_button.clicked.connect(self.accept)

        self.setLayout(layout)
        self.setMinimumWidth(600)

    def set_scan_worker(self, worker: ScanWorker) -> None:
        assert self.__scan_worker is None
        if worker:
            self.__scan_worker = worker
            worker.scan_finished.connect(self.__on_scan_worker_scan_finished)
            worker.info_changed.connect(self.__on_scan_worker_info_changed)
            self.finished.connect(worker.cancel, Qt.DirectConnection)

    def unset_scan_worker(self) -> None:
        assert self.__scan_worker is not None
        self.__scan_worker.disconnect(self)
        self.disconnect(self.__scan_worker)
        self.__scan_worker = None

    def __on_scan_worker_scan_finished(self) -> None:
        if self.__scan_worker.elapsed_time_sec < self.MAX_SCAN_TIME_SEC_TO_AUTOCLOSE:
            self.accept()
        else:
            self.__close_button.setText('Close')
        log.info('Scan finished in %s.', self.__scan_worker.elapsed_time_str)

    def __on_scan_worker_info_changed(self, info: ScanWorker.Info) -> None:
        self.__step.setText(info.step_name)
        self.__disk.setText(info.disk_name)
        self.__tutorial_path.setText(info.tutorial_path)
        self.__tutorial_name.setText(info.tutorial_name)
        self.__elapsed_time.setText(self.__scan_worker.elapsed_time_str)

        if info.folder_count > 0:
            self.__folder_progress.setMaximum(info.folder_count)
            self.__folder_progress.setValue(info.folder_index)
        else:
            self.__folder_progress.setMaximum(0)
            self.__folder_progress.setValue(-1)

    def reset(self):
        self.__step.clear()
        self.__disk.clear()
        self.__tutorial_path.clear()
        self.__tutorial_name.clear()
        self.__elapsed_time.clear()
        self.__folder_progress.setEnabled(False)
        self.__folder_progress.reset()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
