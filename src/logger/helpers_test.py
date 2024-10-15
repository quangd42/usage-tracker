from logger.helpers import calc_skipgrams
from logger.types import LoggedKey


def test_get_skipgram():
    log = [
        LoggedKey('c'),
        LoggedKey('r'),
        LoggedKey('t'),
        LoggedKey('s'),
        LoggedKey('c'),
        LoggedKey('t'),
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
