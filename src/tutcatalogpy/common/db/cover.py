from enum import Enum
from typing import Optional

from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Integer, LargeBinary, Text

from tutcatalogpy.common.db.base import Base


class Cover(Base):

    class FileFormat(bytes, Enum):
        file_name: Optional[str]  # file name

        def __new__(cls, value: int, file_name: Optional[str]):
            obj = bytes.__new__(cls, [value])
            obj._value_ = value
            obj.file_name = file_name
            return obj

        NONE = (0, None)
        JPG = (1, 'cover.jpg')
        PNG = (2, 'cover.png')

    __tablename__ = 'cover'

    id_ = Column('id', Integer, primary_key=True)
    system_id = Column(Text, default=None, nullable=True)
    file_format = Column(Integer, default=FileFormat.NONE, nullable=False)
    created = Column(DateTime, default=None, nullable=True)
    modified = Column(DateTime, default=None, nullable=True)
    size = Column(Integer, default=None, nullable=True)
    data = Column(LargeBinary, default=None, nullable=True)

    @property
    def name(self) -> Optional[str]:
        return Cover.FileFormat(self.file_format).file_name


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
