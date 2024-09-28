from dataclasses import dataclass
from datetime import datetime


@dataclass
class LoggedKey:
    name: str
    time: datetime = datetime.now()


class LoggerException(Exception):
    pass
