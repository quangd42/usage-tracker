import sqlite3
from datetime import datetime

from pynput import keyboard as kb

from logger.helpers import calc_skipgrams
from logger.types import LoggedKey, LoggerException, MODIFIERS

DB_NAME = 'logger.db'


class Logger:
    def __init__(self, session: str) -> None:
        self.listener: kb.Listener = kb.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.log_letters: list[LoggedKey] = []
        self.log_bigrams: list[LoggedKey] = []
        self.log_trigrams: list[LoggedKey] = []
        self.pressed_mods: set[kb.Key | kb.KeyCode] = set()
        self.last_saved: datetime
        self.session_name: str = session
        self.is_paused: bool = False

    def _on_press(self, key: kb.Key | kb.KeyCode | None) -> None:
        # Ignore when logger is paused
        if not key or self.is_paused:
            return

        # If modifier, add to mods
        if key in MODIFIERS:
            self.pressed_mods.add(self.listener.canonical(key))
            return

        # If function keys
        if isinstance(key, kb.Key):
            current_key = LoggedKey(
                name=str(key.name), mods=list(self.pressed_mods), is_letter=False
            )
            print(current_key)
        else:
            can_key = self.listener.canonical(key)
            current_key = LoggedKey(name=can_key.char, mods=list(self.pressed_mods))  # type: ignore

        try:
            # If last keypress is not letter, then no 2gram or 3gram
            last_key = self.log_letters[-1]
            if not last_key.is_letter or not current_key.is_letter:
                raise Exception

            # If current keypress is within 1 second of the last then log 2gram
            last_key_elapsed = current_key.time - last_key.time
            if last_key_elapsed.total_seconds() <= 1:
                self.log_bigrams.append(
                    LoggedKey(name=last_key.name + current_key.name)
                )

            # If keypress before last is not letter, then no 3gram
            before_last_key = self.log_letters[-2]
            if not before_last_key.is_letter:
                raise Exception

            # If current keypress is within 2 seconds of keypress before last then log 3gram
            bf_last_key_elapsed = current_key.time - before_last_key.time
            if bf_last_key_elapsed.total_seconds() <= 2:
                self.log_trigrams.append(
                    LoggedKey(
                        name=before_last_key.name + last_key.name + current_key.name,
                    )
                )

        # If current key is the first or second keypress ever, just ignore
        except IndexError:
            pass
        except Exception:
            pass

        # Finally, log current key to 1gram always
        self.log_letters.append(current_key)

        # Save every 60 seconds and clear logs
        current_interval = current_key.time - self.last_saved
        if current_interval.total_seconds() >= 60:
            self.last_saved = datetime.now()
            self._save_to_db(DB_NAME)
            self.log_letters.clear()
            self.log_bigrams.clear()
            self.log_trigrams.clear()

    def _on_release(self, key: kb.Key | kb.KeyCode | None) -> None:
        if key in MODIFIERS:
            self.pressed_mods.remove(self.listener.canonical(key))

    # TODO: add table for mods, connect with letters
    def _db_init(self, db_name) -> None:
        try:
            con = sqlite3.connect(db_name)
            cur = con.cursor()

            cur.execute(
                'CREATE TABLE IF NOT EXISTS letters (id integer PRIMARY KEY, name, freq, session);'
            )
            cur.execute(
                'CREATE TABLE IF NOT EXISTS bigrams (id integer PRIMARY KEY, name, freq, session);'
            )
            cur.execute(
                'CREATE TABLE IF NOT EXISTS trigrams (id integer PRIMARY KEY, name, freq, session);'
            )
            cur.execute(
                'CREATE TABLE IF NOT EXISTS skipgrams (id integer PRIMARY KEY, name, weight, session);'
            )
            con.close()

        except Exception as exception:
            raise LoggerException(f'__db_init exception: {exception}')

    def _save_to_db(self, db_name) -> None:
        try:
            con = sqlite3.connect(db_name)
            cur = con.cursor()
            logs = {
                'letters': self.log_letters,
                'bigrams': self.log_bigrams,
                'trigrams': self.log_trigrams,
            }
            for log_name in logs:
                for item in logs[log_name]:
                    name = item.name
                    res = cur.execute(
                        f'SELECT id FROM {log_name} WHERE name = ? AND session = ?',
                        (name, self.session_name),
                    ).fetchone()
                    if res is None:
                        cur.execute(
                            f'INSERT INTO {log_name} VALUES(NULL, ?, ?, ?)',
                            (name, 1, self.session_name),
                        )
                    else:
                        cur.execute(
                            f'UPDATE {log_name} SET freq = freq + 1 WHERE id = ?',
                            (res[0],),
                        )
            skipgrams = calc_skipgrams(self.log_letters)
            for key in skipgrams:
                res = cur.execute(
                    'SELECT id FROM skipgrams WHERE name = ? AND session = ?',
                    (key, self.session_name),
                ).fetchone()
                if res is None:
                    cur.execute(
                        'INSERT INTO skipgrams VALUES(NULL, ?, ?, ?)',
                        (key, skipgrams[key], self.session_name),
                    )
                else:
                    cur.execute(
                        'UPDATE skipgrams SET weight = weight + ? WHERE id = ?',
                        (skipgrams[key], res[0]),
                    )

            con.commit()
            con.close()

        except Exception as exception:
            raise LoggerException(f'__save_to_db {exception = }')

    def start(self) -> None:
        if not self.listener.is_alive():
            self.last_saved = datetime.now()
            self.listener.start()
            self.listener.wait()
            self._db_init(DB_NAME)

    def stop(self) -> None:
        if self.listener.is_alive():
            self.end_time = datetime.now()
            self.listener.stop()
            self._save_to_db(DB_NAME)
            print('Session ended.')
        else:
            raise LoggerException('Logging is not in session.')

    def pause(self) -> None:
        if self.listener.is_alive():
            self.is_paused = True
            print('Session paused...')
        else:
            raise LoggerException('Logging is not in session.')

    def resume(self) -> None:
        if self.listener.is_alive():
            self.is_paused = False
            print('Session resumed...')
        else:
            raise LoggerException('Logging is not in session.')
