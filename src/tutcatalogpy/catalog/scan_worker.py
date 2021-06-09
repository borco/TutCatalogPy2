import logging
from datetime import timedelta
from pathlib import Path
from time import perf_counter_ns
from typing import List, Tuple

from humanize import precisedelta
from PySide2.QtCore import QObject, QThread, Signal

from tutcatalogpy.catalog.db.dal import dal
from tutcatalogpy.catalog.db.disk import Disk
from tutcatalogpy.catalog.db.folder import Folder
from tutcatalogpy.catalog.scan_config import ScanConfig, scan_config
from tutcatalogpy.common.files import get_creation_datetime, get_modification_datetime, get_folder_size


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ScanWorker(QObject):
    class Progress:
        disk_name: str = ''
        step_name: str = ''
        folder_parent: str = ''
        folder_name: str = ''
        folder_count: int = 0
        folder_index: int = 0

    scan_started = Signal()
    scan_finished = Signal()
    progress_changed = Signal(Progress)

    def __init__(self):
        super().__init__()
        self.__scanning: bool = False
        self.__cancel: bool = False

    @property
    def scanning(self) -> bool:
        return self.__scanning

    @property
    def elapsed_time_str(self) -> str:
        return str(precisedelta(timedelta(milliseconds=self.elapsed_time_msec)))

    @property
    def elapsed_time_sec(self) -> int:
        return (perf_counter_ns() - self.__scan_start) // 1_000_000_000

    @property
    def elapsed_time_msec(self) -> int:
        return (perf_counter_ns() - self.__scan_start) // 1_000_000

    def cancel(self) -> None:
        self.__cancel = True

    def scan(self, mode: ScanConfig.Mode) -> None:
        if self.__scanning:
            log.warning('scan already in progress; ignoring new scan request.')
            return

        self.scan_started.emit()

        log.info('Starting %s scan.', mode.name)
        self.__scan_start = perf_counter_ns()
        self.__scanning = True
        self.__cancel = False

        self.__progress = self.Progress()

        session = None

        try:
            session = dal.Session()
            self.__scan(session, mode)
        except Exception:
            log.exception('Scan failed.')
        finally:
            if session:
                session.close()

        if self.__cancel:
            log.warning('Scan canceled.')
        else:
            log.debug('Scan finished.')

        self.__scanning = False

        self.scan_finished.emit()

    def update_folder_details(self, folders: List[Tuple[str, str, str]]) -> None:
        if self.__scanning:
            log.warning('scan already in progress; ignoring new scan request.')
            return

        self.scan_started.emit()

        self.__scan_start = perf_counter_ns()
        self.__scanning = True
        self.__cancel = False

        progress = self.Progress()
        progress.step_name = 'Updating Folder Details'
        progress.folder_count = len(folders)

        session = None

        try:
            session = dal.Session()
            for index, (disk_parent, disk_name, folder_parent, folder_name) in enumerate(folders, start=1):
                progress.disk_name = disk_name
                progress.folder_parent = folder_parent
                progress.folder_name = folder_name
                progress.folder_index = index
                self.progress_changed.emit(progress)

                if self.__cancel:
                    break
                query = (
                    session
                    .query(
                        Folder,
                        Disk)
                    .join(Disk)
                    .filter(
                        Disk.disk_parent == disk_parent,
                        Disk.disk_name == disk_name,
                        Folder.folder_parent == folder_parent,
                        Folder.folder_name == folder_name
                    )
                    .first()
                )
                if query:
                    folder, disk = query
                    self.__update_folder_details(session, folder, disk)
                    log.info('Updated folder details: %s | %s | %s | %s', disk_parent, disk_name, folder_parent, folder_name)
                else:
                    log.warning('Could not find folder in db: %s | %s | %s | %s', disk_parent, disk_name, folder_parent, folder_name)
        except Exception:
            log.exception('Update failed.')
        finally:
            if session:
                session.close()

        if self.__cancel:
            log.warning('Update canceled.')
        else:
            log.debug('Update finished.')

        self.__scanning = False

        self.scan_finished.emit()

    def __scan(self, session, mode: ScanConfig.Mode) -> None:
        self.__scan_disks(session)
        self.__scan_folders(session, mode)
        self.__scan_folders_details(session, mode)

    def __scan_disks(self, session) -> None:
        session.query(Disk).update({Disk.online: False})
        session.commit()

        for disk in session.query(Disk):
            disk.online = disk.path().exists()

        session.commit()

    def __scan_folders(self, session, mode: ScanConfig.Mode) -> None:
        self.__progress.step_name = 'Folders'

        self.__progress.folder_index = 0
        for disk in session.query(Disk):
            if not disk.online:
                log.debug('Skipping offline %s', disk.disk_name)
                continue

            if (disk.location == Disk.Location.LOCAL and not scan_config.can_scan(mode, ScanConfig.Option.LOCAL_DISKS)):
                log.debug('Skipping local %s', disk.disk_name)
                continue

            if (disk.location == Disk.Location.REMOTE and not scan_config.can_scan(mode, ScanConfig.Option.REMOTE_DISKS)):
                log.debug('Skipping remote %s', disk.disk_name)
                continue

            if (not disk.checked and not scan_config.can_scan(mode, ScanConfig.Option.UNCHECKED_DISKS)):
                log.debug('Skipping unchecked %s', disk.disk_name)
                continue

            self.__scan_folders_on_disk(mode, session, disk)

        log.info('Scanned %s folders for basic info in %s.', self.__progress.folder_index, self.elapsed_time_str)

    def __scan_folders_on_disk(self, mode, session, disk) -> None:
        if self.__cancel:
            return

        log.debug('Scanning %s', disk.disk_name)

        (
            session
            .query(Folder)
            .filter(Folder.disk_id == disk.id_)
            .update({Folder.status: Folder.Status.UNKNOWN})
        )

        self.__scan_folders_on_path(mode, session, disk, disk.path(), disk.depth)

        # delete folders that still have their status set to UNKNOWN
        # we must use 'session.delete()' to make sqlachemy delete the associated data
        for folder in session.query(Folder).filter(Folder.disk_id == disk.id_).filter(Folder.status == Folder.Status.UNKNOWN):
            session.delete(folder)

        session.commit()

    def __scan_folders_on_path(self, mode, session, disk: Disk, path: Path, depth: int) -> None:
        if self.__cancel:
            return

        self.__progress.disk_name = disk.disk_name

        for p in path.iterdir():
            if self.__cancel:
                return
            if p.is_dir():
                if depth == 0:
                    self.__update_folder(mode, session, disk, p)
                    QThread.yieldCurrentThread()
                else:
                    # if depth == self.depth:
                    #     print(f'publisher: {item.name}')
                    self.__scan_folders_on_path(mode, session, disk, p, depth - 1)

    def __update_folder(self, mode, session, disk: Disk, path: Path) -> None:
        relative_path = path.relative_to(disk.path())
        folder_parent = str(relative_path.parent)
        folder_name = str(relative_path.name)
        stat = path.stat()
        modified = get_modification_datetime(stat)
        created = get_creation_datetime(stat)
        system_id = str(stat.st_ino)

        folder: Folder = (
            session
            .query(Folder)
            .filter(Folder.disk_id == disk.id_)
            .filter(Folder.system_id == system_id)
            .first()
        )

        if folder is None:
            folder = (
                session
                .query(Folder)
                .filter(Folder.disk_id == disk.id_)
                .filter(Folder.folder_parent == folder_parent)
                .filter(Folder.folder_name == folder_name)
                .first()
            )

            if folder is None:
                log.debug('Found new folder: %s/%s', folder_parent, folder_name)
                folder = Folder(
                    folder_parent=folder_parent,
                    folder_name=folder_name,
                    disk_id=disk.id_,
                    system_id=system_id,
                    status=Folder.Status.NEW.value,
                    created=created,
                    modified=modified,
                )
                session.add(folder)
            else:
                log.debug('Found new folder with old name: %s/%s', folder_parent, folder_name)
                folder.system_id = system_id
                folder.status = Folder.Status.NEW.value
                folder.created = created
                folder.modified = modified
        else:
            folder.status = Folder.Status.OK.value

            if folder.modified != modified:
                log.debug('Found updated folder: %s', path)
                folder.modified = modified
                folder.status = Folder.Status.CHANGED.value

            # if both modified and renamed, we keep the RENAMED status and modified value
            if folder.folder_name != folder_name or folder.folder_parent != folder_parent:
                log.debug('Found renamed folder: %s/%s-> %s/%s', folder.folder_parent, folder.folder_name, folder_parent, folder_name)
                folder.folder_parent = folder_parent
                folder.folder_name = folder_name
                folder.status = Folder.Status.RENAMED.value

        session.commit()

        self.__progress.folder_parent = folder.folder_parent
        self.__progress.folder_name = folder.folder_name
        # QThread.msleep(100)

        self.progress_changed.emit(self.__progress)
        self.__progress.folder_index += 1

    def __scan_folders_details(self, session, mode: ScanConfig.Mode) -> None:
        if not scan_config.can_scan(mode, ScanConfig.Option.FOLDER_DETAILS):
            log.info('Skipping folder details.')
            return

        self.__progress.folder_index = 0
        self.__progress.step_name = 'Folder details'

        query = (
            session
            .query(
                Folder,
                Disk)
            .join(Disk)
            .filter(Disk.online == True)
        )

        if scan_config.can_scan(mode, ScanConfig.Option.LOCAL_DISKS) and not scan_config.can_scan(mode, ScanConfig.Option.REMOTE_DISKS):
            query = query.filter(Disk.location == Disk.Location.LOCAL)
        elif not scan_config.can_scan(mode, ScanConfig.Option.LOCAL_DISKS) and scan_config.can_scan(mode, ScanConfig.Option.REMOTE_DISKS):
            query = query.filter(Disk.location == Disk.Location.REMOTE)

        if not scan_config.can_scan(mode, ScanConfig.Option.UNCHECKED_DISKS):
            query = query.filter(Disk.checked == True)

        folder_count = query.count()
        log.info('Getting details for %s folders.', folder_count)

        self.__progress.folder_count = folder_count

        folder: Folder
        disk: Disk
        for folder, disk in query:
            if self.__cancel:
                break

            if folder.status != Folder.Status.OK.value or not folder.size:
                if scan_config.can_scan(mode, ScanConfig.Option.FOLDER_DETAILS):
                    self.__update_folder_details(session, folder, disk)

            self.__progress.disk_name = disk.disk_name
            self.__progress.folder_parent = folder.folder_parent
            self.__progress.folder_name = folder.folder_name
            self.progress_changed.emit(self.__progress)
            self.__progress.folder_index += 1
            # QThread.msleep(100)

    def __update_folder_details(self, session, folder, disk):
        path = Path(disk.disk_parent) / disk.disk_name / folder.folder_parent / folder.folder_name
        folder.size = get_folder_size(path)
        session.commit()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
