from datetime import datetime
from pynput import keyboard
import sqlite3

from .helpers import get_skipgram

DB_NAME = "logger.db"


class Logger:
    def __init__(self) -> None:
        self.listener: keyboard.Listener = keyboard.Listener(on_press=self.__on_press)
        self.log_1gram: list[dict] = []
        self.log_2gram: list[dict] = []
        self.log_3gram: list[dict] = []
        self.last_saved: datetime

    def __on_press(self, key) -> None:
        try:
            # Guard clause for special keys
            if key == keyboard.Key.space:
                key = " "
            else:
                key = key.char

            current_key = {"name": key, "time": datetime.now()}

            try:
                # If current keypress is within 1 second of the last then log 2gram
                last_key = self.log_1gram[-1]
                last_key_elapsed = current_key["time"] - last_key["time"]
                if last_key_elapsed.total_seconds() <= 1:
                    self.log_2gram.append(
                        {
                            "name": last_key["name"] + current_key["name"],
                            "time": current_key["time"],
                        }
                    )

                # If current keypress is within 2 seconds of keypress before last
                # then log 3gram
                before_last_key = self.log_1gram[-2]
                bf_last_key_elapsed = current_key["time"] - before_last_key["time"]
                if bf_last_key_elapsed.total_seconds() <= 2:
                    self.log_3gram.append(
                        {
                            "name": before_last_key["name"]
                            + last_key["name"]
                            + current_key["name"],
                            "time": current_key["time"],
                        }
                    )

            # If current key is the first or second keypress ever, just ignore
            except IndexError:
                pass

            # Finally, log current key to 1gram always
            self.log_1gram.append(current_key)

            # Save every 60 seconds and clear logs
            current_interval = current_key["time"] - self.last_saved
            if current_interval.total_seconds() >= 60:
                self.last_saved = datetime.now()
                # print(self.log_1gram)
                # print(self.log_2gram)
                # print(self.log_3gram)
                self.__save_to_db(DB_NAME)
                self.log_1gram.clear()
                self.log_2gram.clear()
                self.log_3gram.clear()

        except AttributeError:
            pass
        except Exception as exception:
            print(f"on_press exception: {exception}")

    def __db_init(self, db_name) -> None:
        try:
            con = sqlite3.connect(db_name)
            cur = con.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS t1gram (name UNIQUE, freq);")
            cur.execute("CREATE TABLE IF NOT EXISTS t2gram (name UNIQUE, freq);")
            cur.execute("CREATE TABLE IF NOT EXISTS t3gram (name UNIQUE, freq);")
            cur.execute("CREATE TABLE IF NOT EXISTS skipgram (name UNIQUE, weight);")
            con.close()

        except Exception as exception:
            print(f"__db_init exception: {exception}")

    def __save_to_db(self, db_name) -> None:
        try:
            con = sqlite3.connect(db_name)
            cur = con.cursor()
            for index, log in enumerate(
                [self.log_1gram, self.log_2gram, self.log_3gram]
            ):
                for item in log:
                    name = item["name"]
                    res = cur.execute(
                        f"SELECT * FROM t{index+1}gram WHERE name = ?",
                        (name,),
                    ).fetchone()
                    if res is None:
                        cur.execute(
                            f"INSERT INTO t{index+1}gram VALUES(?, ?)",
                            (name, 1),
                        )
                    else:
                        cur.execute(
                            f"UPDATE t{index+1}gram SET freq = freq + 1 WHERE name = ?",
                            (name,),
                        )
            skipgram = get_skipgram(self.log_1gram)
            for key in skipgram:
                res = cur.execute(
                    "SELECT * FROM skipgram WHERE name = ?", (key,)
                ).fetchone()
                if res is None:
                    cur.execute(
                        "INSERT INTO skipgram VALUES(?, ?)",
                        (key, skipgram[key]),
                    )
                else:
                    cur.execute(
                        "UPDATE skipgram SET weight = weight + ? WHERE name = ?",
                        (skipgram[key], key),
                    )

            con.commit()
            con.close()

        except Exception as exception:
            print(f"__save_to_db {exception = }")

    def start(self) -> None:
        if not self.listener.is_alive():
            self.last_saved = datetime.now()
            self.listener.start()
            self.listener.wait()
            self.__db_init(DB_NAME)
        else:
            print("Logger is already running...")

    def stop(self) -> None:
        if self.listener.is_alive():
            self.end_time = datetime.now()
            self.listener.stop()
            # print(self.log_1gram)
            # print(self.log_2gram)
            # print(self.log_3gram)
            self.__save_to_db(DB_NAME)
            print("Session ended.")
        else:
            raise Exception("Logging is not in session.")
