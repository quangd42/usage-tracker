import sqlite3

from click import ClickException


def get_stat_from_db(
    session: str, stat_name: str, limit: int, sort_by: str, db_name: str
) -> list[tuple[str, str]]:
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    if stat_name == "letters":
        stat_name = "unigrams"

    value_name = sort_by
    if value_name == "value":
        if stat_name == "skipgrams":
            value_name = "weight"
        else:
            value_name = "freq"

    try:
        data = cur.execute(
            f"SELECT name, {value_name} FROM {stat_name} WHERE session = '{session}'  ORDER BY {value_name} DESC LIMIT {limit}"
        )
        col_names = tuple([column[0] for column in data.description])
        stat = data.fetchall()
        stat.insert(0, col_names)
    except Exception as e:
        raise ClickException(f"Error getting stats: {e}")

    return stat


def get_session_list(db_name: str) -> list[str]:
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # NOTE: res is a list of tuples so it's best to convert to list of string?
    try:
        res = cur.execute("SELECT DISTINCT session from unigrams").fetchall()
    except Exception as e:
        raise ClickException(f"Error getting sessions: {e}")
    return [session[0] for session in res]
