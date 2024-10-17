import platform
from dataclasses import dataclass, field
from datetime import datetime

from pynput import keyboard as kb

MODIFIERS: set[kb.KeyCode] = set(
    [
        kb.Key.alt,
        kb.Key.alt_gr,
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
    key: kb.Key | kb.KeyCode
    mods: set[kb.KeyCode]
    time: datetime = field(default_factory=datetime.now)
    name: str = field(init=False)
    is_letter: bool = field(init=False)

    def __post_init__(self) -> None:
        if isinstance(self.key, kb.Key):
            self.name = f'<{self.key.name}>'
            self.is_letter = False
        elif isinstance(self.key, kb.KeyCode):
            self.is_letter = True
            # Return canonical of macOS opt + key and shift + key
            if platform.system() == 'Darwin' and self.key.vk is not None:
                self.name = self.macOS_vk_to_char(self.key.vk)
            # Return canonical of shift + key for other platforms
            elif self.key.char is not None:
                self.name = self.unshift_char(self.key.char)
            else:
                raise Exception(f'key.char is None: {self.key}')
        else:
            raise Exception(f'Invalid key: {self.key}')

    @classmethod
    def macOS_vk_to_char(cls, vk_code: int) -> str:
        # ruff: noqa : E701
        # fmt: off
        match vk_code:
            case 0x00: return 'a'
            case 0x01: return 's'
            case 0x02: return 'd'
            case 0x03: return 'f'
            case 0x04: return 'h'
            case 0x05: return 'g'
            case 0x06: return 'z'
            case 0x07: return 'x'
            case 0x08: return 'c'
            case 0x09: return 'v'
            case 0x0B: return 'b'
            case 0x0C: return 'q'
            case 0x0D: return 'w'
            case 0x0E: return 'e'
            case 0x0F: return 'r'
            case 0x10: return 'y'
            case 0x11: return 't'
            case 0x12: return '1'
            case 0x13: return '2'
            case 0x14: return '3'
            case 0x15: return '4'
            case 0x16: return '6'
            case 0x17: return '5'
            case 0x18: return '='
            case 0x19: return '9'
            case 0x1A: return '7'
            case 0x1B: return '-'
            case 0x1C: return '8'
            case 0x1D: return '0'
            case 0x1E: return ']'
            case 0x1F: return 'o'
            case 0x20: return 'u'
            case 0x21: return '['
            case 0x22: return 'i'
            case 0x23: return 'p'
            case 0x25: return 'l'
            case 0x26: return 'j'
            case 0x27: return '\''
            case 0x28: return 'k'
            case 0x29: return ';'
            case 0x2A: return '\\'
            case 0x2B: return ','
            case 0x2C: return '/'
            case 0x2D: return 'n'
            case 0x2E: return 'm'
            case 0x2F: return '.'
            case 0x32: return '`'
            # Add more special keys if needed
            case _: raise Exception('vk cannot be converted')
        # fmt: on

    @classmethod
    def unshift_char(cls, s: str) -> str:
        # ruff: noqa : E701
        # fmt: off
        match s:
            case '!': return '1'
            case '@': return '2'
            case '#': return '3'
            case '$': return '4'
            case '%': return '5'
            case '^': return '6'
            case '&': return '7'
            case '*': return '8'
            case '(': return '9'
            case ')': return '0'
            case '_': return '-'
            case '+': return '='
            case '{': return '['
            case '}': return ']'
            case '|': return '\\'
            case ':': return ';'
            case '"': return "'"
            case '<': return ','
            case '>': return '.'
            case '?': return '/'
            case '~': return '`'
            case _: return s.lower()
        # fmt: on


@dataclass
class Ngram:
    name: str
    time: datetime = datetime.now()
