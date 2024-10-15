from datetime import datetime

from pynput import keyboard as kb

from db.queries import DatabaseQueries
from logger.types import MODIFIERS, LoggedKey, LoggerException


class Logger:
    def __init__(self, queries: DatabaseQueries, session: str) -> None:
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
        self.db = queries

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
                name=f'<{str(key.name)}>', mods=list(self.pressed_mods), is_letter=False
            )
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
            self._save_to_db()
            self.log_letters.clear()
            self.log_bigrams.clear()
            self.log_trigrams.clear()

    def _on_release(self, key: kb.Key | kb.KeyCode | None) -> None:
        if key in MODIFIERS:
            self.pressed_mods.remove(self.listener.canonical(key))

    def _save_to_db(self) -> None:
        try:
            self.db.save_log_letters(self.log_letters, self.session_name)
            self.db.save_log_bigrams(self.log_bigrams, self.session_name)
            self.db.save_log_trigrams(self.log_trigrams, self.session_name)
            self.db.save_log_skipgram(self.log_letters, self.session_name)
            self.db.conn.commit()

        except Exception as exception:
            raise LoggerException(f'_save_to_db {exception = }')

    def start(self) -> None:
        if not self.listener.is_alive():
            self.last_saved = datetime.now()
            self.listener.start()
            self.listener.wait()

    def stop(self) -> None:
        if self.listener.is_alive():
            self.end_time = datetime.now()
            self.listener.stop()
            self._save_to_db()
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
