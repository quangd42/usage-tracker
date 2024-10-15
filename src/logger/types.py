from dataclasses import dataclass, field
from datetime import datetime

from pynput import keyboard as kb

MODIFIERS: set[kb.KeyCode] = set(
    [
        kb.Key.alt_gr,
        kb.Key.alt,
        kb.Key.alt_l,
        kb.Key.alt_r,
        kb.Key.cmd,
        kb.Key.cmd_l,
        kb.Key.cmd_r,
        kb.Key.ctrl,
        kb.Key.ctrl_l,
        kb.Key.ctrl_r,
        kb.Key.shift,
        kb.Key.shift_l,
        kb.Key.shift_r,
    ]
)


@dataclass
class LoggedKey:
    name: str
    mods: list[kb.Key | kb.KeyCode] = field(default_factory=list)
    time: datetime = datetime.now()
    is_letter: bool = True


class LoggerException(Exception):
    pass
