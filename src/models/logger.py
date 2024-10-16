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

    def _normalize_name(self) -> None:
        match self.name:
            case '!':
                self.name = '1'
            case '@':
                self.name = '2'
            case '#':
                self.name = '3'
            case '$':
                self.name = '4'
            case '%':
                self.name = '5'
            case '^':
                self.name = '6'
            case '&':
                self.name = '7'
            case '*':
                self.name = '8'
            case '(':
                self.name = '9'
            case ')':
                self.name = '0'
            case '_':
                self.name = '-'
            case '+':
                self.name = '='
            case '{':
                self.name = '['
            case '}':
                self.name = ']'
            case '|':
                self.name = '\\'
            case ':':
                self.name = ';'
            case '"':
                self.name = "'"
            case '<':
                self.name = ','
            case '>':
                self.name = '.'
            case '?':
                self.name = '/'
            case '~':
                self.name = '`'

    def __post_init__(self) -> None:
        self._normalize_name()
