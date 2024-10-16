import sqlite3
from typing import Any

from logger.helpers import calc_skipgrams
from models.genkey import GenkeyOutput
from models.logger import LoggedKey


class DatabaseQueries:
    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)
        self._db_init()

    def _db_init(self) -> None:
        cur = self.conn.cursor()
        try:
            queries = """
                CREATE TABLE IF NOT EXISTS letters (
                    id INT PRIMARY KEY,
                    name TEXT,
                    timestamp TIMESTAMP,
                    is_letter INT,
                    mods TEXT,
                    session TEXT
                );

                CREATE TABLE IF NOT EXISTS bigrams (
                    id INT PRIMARY KEY,
                    name TEXT,
                    timestamp TIMESTAMP,
                    session TEXT
                );

                CREATE TABLE IF NOT EXISTS trigrams (
                    id INT PRIMARY KEY,
                    name TEXT,
                    timestamp TIMESTAMP,
                    session TEXT
                );

                CREATE TABLE IF NOT EXISTS skipgrams (
                    id INT PRIMARY KEY,
                    name TEXT,
                    weight NUM,
                    session TEXT
                );
            """
            commands = queries.split(';')

            for command in commands:
                cur.execute(command)

        except Exception as e:
            raise Exception(f'db_init exception: {e}')

    def save_log_letters(self, log: list[LoggedKey], session_name: str) -> None:
        cur = self.conn.cursor()
        for item in log:
            try:
                mod_names = [mod.name for mod in item.mods]  # pyright: ignore[reportAttributeAccessIssue]
            except AttributeError:
                raise Exception('Mod is not kb.Key')
            mods = ','.join(sorted(mod_names))
            cur.execute(
                'INSERT INTO letters VALUES (NULL, ?, ?, ?, ?, ?)',
                (
                    item.name,
                    item.time,
                    item.is_letter,
                    mods,
                    session_name,
                ),
            )

    def save_log_ngrams(
        self, log_name: str, log: list[LoggedKey], session_name: str
    ) -> None:
        cur = self.conn.cursor()
        for item in log:
            cur.execute(
                f'INSERT INTO {log_name} VALUES(NULL, ?, ?, ?)',
                (item.name, item.time, session_name),
            )

    def save_log_bigrams(self, log: list[LoggedKey], session_name: str) -> None:
        self.save_log_ngrams('bigrams', log, session_name)

    def save_log_trigrams(self, log: list[LoggedKey], session_name: str) -> None:
        self.save_log_ngrams('trigrams', log, session_name)

    def save_log_skipgram(self, log: list[LoggedKey], session_name: str) -> None:
        cur = self.conn.cursor()
        skipgrams = calc_skipgrams(log)
        for key in skipgrams:
            res = cur.execute(
                'SELECT id FROM skipgrams WHERE name = ? AND session = ?',
                (key, session_name),
            ).fetchone()
            if res is None:
                cur.execute(
                    'INSERT INTO skipgrams VALUES(NULL, ?, ?, ?)',
                    (key, skipgrams[key], session_name),
                )
            else:
                cur.execute(
                    'UPDATE skipgrams SET weight = weight + ? WHERE id = ?',
                    (skipgrams[key], res[0]),
                )

    def get_stats(
        self, session: str, stat_name: str, sort_by: str, limit: int = -1
    ) -> list[tuple[str, Any]]:
        cur = self.conn.cursor()
        stat: list[Any] = []
        query: str = ''

        if sort_by == 'name':
            sort_key = '1 ASC'
        elif sort_by == 'value':
            sort_key = '2 DESC'
        else:
            raise Exception('invalid sort_by value')

        match stat_name:
            case 'letters':
                query = f"""
                            SELECT name, count(name) as freq
                            FROM letters
                            WHERE session = ? AND is_letter = 1
                            GROUP BY name
                            ORDER BY {sort_key}
                            LIMIT ?
                        """
            case 'bigrams' | 'trigrams':
                query = f"""
                            SELECT name, count(name) as freq
                            FROM {stat_name}
                            WHERE session = ?
                            GROUP BY name
                            ORDER BY {sort_key}
                            LIMIT ?
                        """
            case 'skipgrams':
                query = f"""
                        SELECT name, weight FROM skipgrams
                        WHERE session = ?
                        ORDER BY {sort_key}
                        LIMIT ?
                    """

        try:
            data = cur.execute(
                query,
                (
                    session,
                    limit,
                ),
            )
            col_names = tuple([column[0] for column in data.description])
            stat = data.fetchall()
            stat.insert(0, col_names)

        except Exception as e:
            raise Exception(f'Error getting stats: {e}')

        return stat

    def list_sessions(self) -> list[str]:
        cur = self.conn.cursor()

        # NOTE: res is a list of tuples so it's best to convert to list of string?
        try:
            res = cur.execute('SELECT DISTINCT session from letters').fetchall()
        except Exception:
            raise Exception('No saved sessions.')
        return [session[0] for session in res]

    def delete_session(self, session: str) -> None:
        cur = self.conn.cursor()

        stat_names = GenkeyOutput.list_keys()
        try:
            for stat_name in stat_names:
                query = f"""
                        DELETE FROM {stat_name}
                        WHERE session = ?
                    """
                cur.execute(query, (session,))

        except Exception as e:
            raise Exception(f'Error deleting session: {e}')

    def get_genkey_stats(self, session: str) -> GenkeyOutput:
        letters = self.get_stats(session=session, stat_name='letters', sort_by='name')
        bigrams = self.get_stats(session=session, stat_name='bigrams', sort_by='name')
        trigrams = self.get_stats(session=session, stat_name='trigrams', sort_by='name')
        skipgrams = self.get_stats(
            session=session, stat_name='skipgrams', sort_by='name'
        )

        # NOTE: the first item is the header
        return GenkeyOutput(
            dict(letters[1:]),
            dict(bigrams[1:]),
            dict(trigrams[1:]),
            dict(skipgrams[1:]),
        )
