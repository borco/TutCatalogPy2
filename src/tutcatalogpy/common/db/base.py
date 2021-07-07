from typing import Final

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

FIELD_SEPARATOR: Final[str] = ','
