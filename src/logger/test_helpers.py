from datetime import datetime
from .helpers import get_skipgram


def test_get_skipgram():
    log = [
        {"name": "c", "datetime": datetime.now()},
        {"name": "r", "datetime": datetime.now()},
        {"name": "t", "datetime": datetime.now()},
        {"name": "s", "datetime": datetime.now()},
        {"name": "c", "datetime": datetime.now()},
        {"name": "t", "datetime": datetime.now()},
    ]

    weight = []
    for i in range(10):
        weight.append(1 / 2**i)

    expected = {
        "cr": 0.5,
        "rt": 0.5625,
        "ct": 0.78125,
        "ts": 0.5,
        "rs": 0.25,
        "cs": 0.125,
        "sc": 0.5,
        "tc": 0.25,
        "rc": 0.125,
        "cc": 0.0625,
        "st": 0.25,
        "tt": 0.125,
    }

    assert get_skipgram(log) == expected


if __name__ == "__main__":
    test_get_skipgram()
