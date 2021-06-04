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
    class Info:
        disk_name: str = ''
        step_name: str = ''
        tutorial_path: str = ''
        tutorial_name: str = ''
        folder_count: int = 0
        folder_index: int = 0

    scan_started = Signal()
    scan_finished = Signal()
    disks_scan_finished = Signal()
    folders_scan_finished = Signal()
    folders_details_scan_finished = Signal()
    folder_details_updated = Signal(str, str, str, str)
    info_changed = Signal(Info)

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

        self.__info = self.Info()

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

        info = self.Info()
        info.step_name = 'Updating Folder Details'
        info.folder_count = len(folders)

        session = None

        try:
            session = dal.Session()
            for index, (disk_parent, disk_name, tutorial_path, tutorial_name) in enumerate(folders, start=1):
                info.disk_name = disk_name
                info.tutorial_path = tutorial_path
                info.tutorial_name = tutorial_name
                info.folder_index = index
                self.info_changed.emit(info)

                if self.__cancel:
                    break
                query = (
                    session
                    .query(
                        Folder,
                        Disk)
                    .join(Disk)
                    .filter(
                        Disk.path_parent == disk_parent,
                        Disk.path_name == disk_name,
                        Folder.tutorial_path == tutorial_path,
                        Folder.tutorial_name == tutorial_name
                    )
                    .first()
                )
                if query:
                    folder, disk = query
                    self.__update_folder_details(session, folder, disk)
                    self.folder_details_updated.emit(disk_parent, disk_name, tutorial_path, tutorial_name)
                    log.info('Updated folder details: %s | %s | %s | %s', disk_parent, disk_name, tutorial_path, tutorial_name)
                else:
                    log.warning('Could not find folder in db: %s | %s | %s | %s', disk_parent, disk_name , tutorial_path, tutorial_name)
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

        self.folders_details_scan_finished.emit()
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

        self.disks_scan_finished.emit()

    def __scan_folders(self, session, mode: ScanConfig.Mode) -> None:
        self.__info.step_name = 'Folders'

        self.__info.folder_index = 0
        for disk in session.query(Disk):
            if not disk.online:
                log.debug('Skipping offline %s', disk.path_name)
                continue

            if (disk.location == Disk.Location.LOCAL and not scan_config.can_scan(mode, ScanConfig.Option.LOCAL_DISKS)):
                log.debug('Skipping local %s', disk.path_name)
                continue

            if (disk.location == Disk.Location.REMOTE and not scan_config.can_scan(mode, ScanConfig.Option.REMOTE_DISKS)):
                log.debug('Skipping remote %s', disk.path_name)
                continue

            if (not disk.enabled and not scan_config.can_scan(mode, ScanConfig.Option.DISABLED_DISKS)):
                log.debug('Skipping disable %s', disk.path_name)
                continue

            self.__scan_folders_on_disk(mode, session, disk)

        log.info('Scanned %s folders for basic info in %s.', self.__info.folder_index, self.elapsed_time_str)

        self.folders_scan_finished.emit()

    def __scan_folders_on_disk(self, mode, session, disk) -> None:
        if self.__cancel:
            return

        log.debug('Scanning %s', disk.path_name)

        (
            session
            .query(Folder)
            .filter(Folder.disk_id == disk.id_)
            .update({Folder.status: Folder.Status.UNKNOWN.value})
        )

        self.__scan_folders_on_path(mode, session, disk, disk.path(), disk.depth)

        # delete folders that still have their status set to UNKNOWN
        (
            session
            .query(Folder)
            .filter(Folder.disk_id == disk.id_)
            .filter(Folder.status == Folder.Status.UNKNOWN.value)
            .delete()
        )

        session.commit()

    def __scan_folders_on_path(self, mode, session, disk: Disk, path: Path, depth: int) -> None:
        if self.__cancel:
            return

        self.__info.disk_name = disk.path_name

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
        tutorial_path = str(relative_path.parent)
        tutorial_name = str(relative_path.name)
        stat = path.stat()
        modified = get_modification_datetime(stat)
        created = get_creation_datetime(stat)
        system_id = str(stat.st_ino)

        folder = (
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
                .filter(Folder.tutorial_path == tutorial_path)
                .filter(Folder.tutorial_name == tutorial_name)
                .first()
            )

            if folder is None:
                log.debug('Found new folder: %s/%s', tutorial_path, tutorial_name)
                folder = Folder(
                    tutorial_path=tutorial_path,
                    tutorial_name=tutorial_name,
                    disk_id=disk.id_,
                    system_id=system_id,
                    status=Folder.Status.NEW.value,
                    created=created,
                    modified=modified,
                )
                session.add(folder)
            else:
                log.debug('Found new folder with old name: %s/%s', tutorial_path, tutorial_name)
                folder.system_id = system_id
                folder.status = Folder.Status.NEW.value
                folder.created = created
                folder.modified = modified
        else:
            folder.status = Folder.Status.UNCHANGED.value

            if folder.modified != modified:
                log.debug('Found updated folder: %s', path)
                folder.modified = modified
                folder.status = Folder.Status.CHANGED.value

            # if both modified and renamed, we keep the RENAMED status and modified value
            if folder.tutorial_name != tutorial_name or folder.tutorial_path != tutorial_path:
                log.debug('Found renamed folder: %s/%s-> %s/%s', folder.tutorial_path, folder.tutorial_name, tutorial_path, tutorial_name)
                folder.tutorial_path = tutorial_path
                folder.tutorial_name = tutorial_name
                folder.status = Folder.Status.RENAMED.value

        session.commit()

        self.__info.tutorial_path = folder.tutorial_path
        self.__info.tutorial_name = folder.tutorial_name
        # QThread.msleep(100)

        self.info_changed.emit(self.__info)
        self.__info.folder_index += 1

    def __scan_folders_details(self, session, mode: ScanConfig.Mode) -> None:
        if not scan_config.can_scan(mode, ScanConfig.Option.FOLDER_DETAILS):
            log.info('Skipping folder details.')
            return

        self.__info.folder_index = 0
        self.__info.step_name = 'Folder details'

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

        if not scan_config.can_scan(mode, ScanConfig.Option.DISABLED_DISKS):
            query = query.filter(Disk.enabled == True)

        folder_count = query.count()
        log.info('Getting details for %s folders.', folder_count)

        self.__info.folder_count = folder_count

        for folder, disk in query:
            if self.__cancel:
                break

            if folder.status != Folder.Status.UNCHANGED.value or not folder.size:
                if scan_config.can_scan(mode, ScanConfig.Option.FOLDER_DETAILS):
                    self.__update_folder_details(session, folder, disk)

            self.__info.disk_name = disk.path_name
            self.__info.tutorial_path = folder.tutorial_path
            self.__info.tutorial_name = folder.tutorial_name
            self.info_changed.emit(self.__info)
            self.__info.folder_index += 1
            # QThread.msleep(100)

        self.folders_details_scan_finished.emit()

    def __update_folder_details(self, session, folder, disk):
        path = Path(disk.path_parent) / disk.path_name / folder.tutorial_path / folder.tutorial_name
        folder.size = get_folder_size(path)
        session.commit()


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
