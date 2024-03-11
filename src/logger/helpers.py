import sqlite3


def get_skipgram(log_1gram: list[dict]) -> dict[str, float]:
    # Skipgram weight: most recent key is 1/2, next key is 1/4
    # and so on up to the most recent 10 keys
    weight = []
    for i in range(10):
        weight.append(1 / 2 ** (i + 1))

    # List of most recent keypress, most recent as 0 index
    last_chars: list[str] = []

    skipgram: dict[str, float] = {}

    for logged_key in log_1gram:
        key_name = logged_key["name"]
        # Go through last_chars, add weight of skipgram
        # `current_key+last_char` to the dict
        for i in range(len(last_chars)):
            try:
                skipgram[last_chars[i] + key_name] += weight[i]
            except KeyError:
                skipgram[last_chars[i] + key_name] = weight[i]

        # Add current key to last_chars list, make sure that it's
        # not more than 10
        last_chars.insert(0, key_name)
        if len(last_chars) > 10:
            last_chars = last_chars[:10]

    return skipgram


def get_stat_from_db(stat_name: str, db_name: str) -> list[tuple]:
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    if stat_name == "letters":
        stat_name = "unigrams"

    stat = cur.execute(f"SELECT * FROM {stat_name}").fetchall()
    return stat
