from datetime import datetime
from pynput import keyboard
from pathlib import Path


class Logger:
    def __init__(self) -> None:
        self.listener: keyboard.Listener = keyboard.Listener(on_press=self.__on_press)
        self.log: list[str] = []
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    def __on_press(self, key) -> None:
        if len(self.log) == 0:
            try:
                self.log.append(key.char)
            except AttributeError:
                pass
        else:
            try:
                self.log[-1] += key.char
            except AttributeError:
                if key == keyboard.Key.space:
                    self.log[-1] += " "
                elif key == keyboard.Key.enter:
                    self.log.append("")
                else:
                    pass
        # finally:
        #     print(f"{key = }")

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
