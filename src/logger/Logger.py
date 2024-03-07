from datetime import datetime, timedelta
from pynput import keyboard
import sqlite3

DB_NAME = "logger.db"


class Logger:
    def __init__(self) -> None:
        self.listener: keyboard.Listener = keyboard.Listener(on_press=self.__on_press)
        self.log_1gram: list[dict] = []
        self.log_2gram: list[dict] = []
        self.log_3gram: list[dict] = []
        self.interval_start_time: datetime = datetime.now()

    def __on_press(self, key):
        try:
            # Guard clause for special keys
            if key == keyboard.Key.space:
                key = " "
            else:
                key = key.char

            current_key = {"name": key, "datetime": datetime.now()}

            # If last keypress is within 1 second of the previous
            try:
                # If previous doen't exist, IndexError will be raised
                last_key = self.log_1gram[-1]
                time_elapsed = current_key["datetime"] - last_key["datetime"]
                if time_elapsed.total_seconds() <= 1:
                    self.log_2gram.append(
                        {
                            "name": last_key["name"] + current_key["name"],
                            "datetime": current_key["datetime"],
                        }
                    )
                    # Same for 3gram
                    before_last_key = self.log_1gram[-2]
                    self.log_3gram.append(
                        {
                            "name": before_last_key["name"]
                            + last_key["name"]
                            + current_key["name"],
                            "datetime": current_key["datetime"],
                        }
                    )

            except IndexError:
                pass

            # Finally, log 1gram always
            self.log_1gram.append(current_key)

            # Save every 60 seconds and clear logs
            if (datetime.now() - self.interval_start_time) / timedelta(seconds=1) >= 5:
                self.interval_start_time = datetime.now()
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
            con.commit()
            con.close()

        except Exception as exception:
            print(f"__save_to_db {exception = }")

    def start(self) -> None:
        if not self.listener.is_alive():
            self.interval_start_time = datetime.now()
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
