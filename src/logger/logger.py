from datetime import datetime

from pynput import keyboard as kb

from db.queries import DatabaseQueries
from models.logger import MODIFIERS, LoggedKey, Ngram


class Logger:
    def __init__(self, queries: DatabaseQueries, session: str) -> None:
        self.listener: kb.Listener = kb.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.log_letters: list[LoggedKey] = []
        self.log_bigrams: list[Ngram] = []
        self.log_trigrams: list[Ngram] = []
        self.pressed_mods: set[kb.KeyCode] = set()
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
                self.pressed_mods.add(self.normalize_mod(key))
                return

        # If function keys
        if isinstance(key, kb.Key):
            current_key = LoggedKey(
                name=f'<{str(key.name)}>', mods=list(self.pressed_mods), is_letter=False
            )
        else:
            can_key = self.listener.canonical(key)
            current_key = LoggedKey(name=can_key.char, mods=list(self.pressed_mods))  # type: ignore

        # Try to log bigram and trigram
        self._log_ngram(current_key)

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
            self.pressed_mods.remove(self.normalize_mod(key))

    @classmethod
    def normalize_mod(cls, mod: kb.KeyCode) -> kb.KeyCode:
        if isinstance(mod, kb.Key):
            match str(mod.name):
                case 'cmd' | 'cmd_l' | 'cmd_r':
                    return kb.Key.cmd
                case 'ctrl' | 'ctrl_l' | 'ctrl_r':
                    return kb.Key.ctrl
                case 'alt' | 'alt_gr' | 'alt_l' | 'alt_r':
                    return kb.Key.alt
                case 'shift' | 'shift_l' | 'shift_r':
                    return kb.Key.shift
        return mod

    def _log_ngram(self, current_key: LoggedKey) -> None:
        # If this is first keypress, no bigram
        if len(self.log_letters) == 0:
            return
        last_key = self.log_letters[-1]
        if not last_key.is_letter or not current_key.is_letter:
            return

        # If current keypress is within 1 second of the last then log 2gram
        last_key_elapsed = current_key.time - last_key.time
        if last_key_elapsed.total_seconds() <= 1:
            self.log_bigrams.append(Ngram(name=last_key.name + current_key.name))

        # Needs at least 2 previous keys to assess trigrams
        if len(self.log_letters) < 2:
            return
        # If keypress before last is not letter, then no 3gram
        before_last_key = self.log_letters[-2]
        if not before_last_key.is_letter:
            return

        # If current keypress is within 2 seconds of keypress before last then log 3gram
        bf_last_key_elapsed = current_key.time - before_last_key.time
        if bf_last_key_elapsed.total_seconds() <= 2:
            self.log_trigrams.append(
                Ngram(
                    name=before_last_key.name + last_key.name + current_key.name,
                )
            )

    def _save_to_db(self) -> None:
        try:
            self.db.save_log_letters(self.log_letters, self.session_name)
            self.db.save_log_bigrams(self.log_bigrams, self.session_name)
            self.db.save_log_trigrams(self.log_trigrams, self.session_name)
            self.db.save_log_skipgram(self.log_letters, self.session_name)
            self.db.conn.commit()

        except Exception as exception:
            raise Exception(f'_save_to_db {exception = }')

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
            raise Exception('Logging is not in session.')

    def pause(self) -> None:
        if self.listener.is_alive():
            self.is_paused = True
            print('Session paused...')
        else:
            raise Exception('Logging is not in session.')

    def resume(self) -> None:
        if self.listener.is_alive():
            self.is_paused = False
            print('Session resumed...')
        else:
            raise Exception('Logging is not in session.')
