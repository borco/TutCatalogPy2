from enum import IntEnum, IntFlag, auto
from typing import Final

from PySide2.QtCore import QSettings


class ScanConfig:
    SETTINGS_GROUP: Final[str] = 'scan_config'
    SETTINGS_STARTUP: Final[str] = 'startup'
    SETTINGS_QUICK: Final[str] = 'quick'
    SETTINGS_EXTENDED: Final[str] = 'extended'

    class Mode(IntEnum):
        STARTUP = auto()
        QUICK = auto()
        EXTENDED = auto()

    class Option(IntFlag):
        NOTHING = 0
        LOCAL_DISKS = auto()
        REMOTE_DISKS = auto()
        UNCHECKED_DISKS = auto()
        FOLDER_DETAILS = auto()

    DEFAULT_STARTUP: Final = (
        Option.NOTHING
    )

    DEFAULT_QUICK: Final = (
        Option.LOCAL_DISKS
        | Option.FOLDER_DETAILS
    )

    DEFAULT_EXTENDED: Final = (
        Option.LOCAL_DISKS
        | Option.REMOTE_DISKS
        | Option.UNCHECKED_DISKS
        | Option.FOLDER_DETAILS
    )

    option: dict[Mode, Option] = {
        Mode.STARTUP: DEFAULT_STARTUP,
        Mode.QUICK: DEFAULT_QUICK,
        Mode.EXTENDED: DEFAULT_EXTENDED,
    }

    def save_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        for key, mode in [
            (ScanConfig.SETTINGS_STARTUP, ScanConfig.Mode.STARTUP),
            (ScanConfig.SETTINGS_QUICK, ScanConfig.Mode.QUICK),
            (ScanConfig.SETTINGS_EXTENDED, ScanConfig.Mode.EXTENDED),
        ]:
            settings.setValue(key, int(self.option[mode]))
        settings.endGroup()

    def load_settings(self, settings: QSettings) -> None:
        settings.beginGroup(self.SETTINGS_GROUP)
        for key, mode, default_value in [
            (ScanConfig.SETTINGS_STARTUP, ScanConfig.Mode.STARTUP, ScanConfig.DEFAULT_STARTUP),
            (ScanConfig.SETTINGS_QUICK, ScanConfig.Mode.QUICK, ScanConfig.DEFAULT_QUICK),
            (ScanConfig.SETTINGS_EXTENDED, ScanConfig.Mode.EXTENDED, ScanConfig.DEFAULT_EXTENDED),
        ]:
            self.option[mode] = ScanConfig.Option(settings.value(key, defaultValue=int(default_value), type=int))
        settings.endGroup()

    def can_scan(self, mode: Mode, option: Option) -> bool:
        return bool(self.option[mode] & option)


scan_config = ScanConfig()
