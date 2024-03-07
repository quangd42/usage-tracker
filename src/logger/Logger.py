from datetime import datetime, timedelta
from pynput import keyboard
from pathlib import Path


class Logger:
    def __init__(self) -> None:
        self.listener: keyboard.Listener = keyboard.Listener(on_press=self.__on_press)
        self.log_1gram: list[dict[str, str | datetime]] = []
        self.log_2gram: list[dict[str, str | datetime]] = []
        self.log_3gram: list[dict[str, str | datetime]] = []

    def __on_press(self, key):
        try:
            # Guard clause for special keys
            if key == keyboard.Key.space:
                key = " "
            else:
                key = key.char

            current_key = {"name": key, "datetime": datetime.now()}

            # Log 2gram if last keypress is within 1 second
            if len(self.log_1gram) > 0:
                last_key = self.log_1gram[-1]
                delta = current_key["datetime"] - last_key["datetime"]
                if delta / timedelta(microseconds=1) <= 100:
                    self.log_2gram.append(
                        {
                            f"{last_key['name']}{current_key['name']}": current_key[
                                "datetime"
                            ]
                        }
                    )

            # Log 3gram if last keypress is within 1 second of the 2gram
            if len(self.log_2gram) > 0:
                last_key = self.log_2gram[-1]
                delta = current_key["datetime"] - last_key["datetime"]
                if delta / timedelta(microseconds=1) <= 100:
                    self.log_3gram.append(
                        {
                            f"{last_key['name']}{current_key['name']}": current_key[
                                "datetime"
                            ]
                        }
                    )

            # Finally, log 1gram always
            self.log_1gram.append(current_key)

        except AttributeError:
            pass

    def start(self) -> None:
        if not self.listener.is_alive():
            self.start_time = datetime.now()
            self.listener.start()
            self.listener.wait()

    def stop(self) -> None:
        if self.listener.is_alive():
            self.end_time = datetime.now()
            self.listener.stop()
            self.__save()

    def __save(self) -> None:
        try:
            if self.log == "" or not self.start_time or not self.end_time:
                raise Exception("Logger has not been run yet.")

            start = self.start_time.strftime("%m%d_%H%M%S")
            end = self.end_time.strftime("%m%d_%H%M%S")
            output_dir = Path("./data")
            Path.mkdir(output_dir, parents=True, exist_ok=True)
            output = Path("./data").resolve() / f"{start}__{end}.txt"

            with open(output, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log))

        except Exception as exception:
            print(f"Exception: {exception}")
