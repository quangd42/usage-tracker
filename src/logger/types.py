from dataclasses import dataclass
from datetime import datetime


@dataclass
class LoggedKey:
    name: str
    time: datetime = datetime.now()
    is_letter: bool = True


class LoggerException(Exception):
    pass
