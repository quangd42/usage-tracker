from ..logger.helpers import calc_skipgrams
from ..models.logger import LoggedKey
from pynput import keyboard as kb


def test_get_skipgram():
    log = [
        LoggedKey(kb.KeyCode.from_char('c')),
        LoggedKey(kb.KeyCode.from_char('r')),
        LoggedKey(kb.KeyCode.from_char('t')),
        LoggedKey(kb.KeyCode.from_char('s')),
        LoggedKey(kb.KeyCode.from_char('c')),
        LoggedKey(kb.KeyCode.from_char('t')),
    ]

    weight = []
    for i in range(10):
        weight.append(1 / 2**i)

    expected = {
        'cr': 0.5,
        'rt': 0.5625,
        'ct': 0.78125,
        'ts': 0.5,
        'rs': 0.25,
        'cs': 0.125,
        'sc': 0.5,
        'tc': 0.25,
        'rc': 0.125,
        'cc': 0.0625,
        'st': 0.25,
        'tt': 0.125,
    }

    assert calc_skipgrams(log) == expected


if __name__ == '__main__':
    test_get_skipgram()
