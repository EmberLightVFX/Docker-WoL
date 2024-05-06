import os
import configparser
import threading
import time


class Settings:
    def __init__(self):
        self._default_settings = {
            "ip_range": "192.168.1.0/24",
        }

        self._thread_started = False
        self._waiting = False

        self._thread_started = False
        self._waiting = False
        self._settings = configparser.ConfigParser()
        self._settings.add_section("Settings")
        self._settings["Settings"] = self._default_settings
        self._settings.add_section("Computers")

        self.load()

    @property
    def ip_range(self) -> str:
        return self._settings.get(
            "Settings",
            "ip_range",
        )

    @ip_range.setter
    def ip_range(self, value: str) -> None:
        self._settings.set(
            "Settings",
            "ip_range",
            value,
        )
        self.on_change()

    def get_list(self, section: str) -> dict[str, str]:
        return dict(self._settings[section].items())

    def set(self, section: str, name: str, value: bool | str):
        self._settings.set(
            section,
            name,
            str(value),
        )
        self.on_change()

    def remove(self, section: str, name: str):
        if self._settings[section].get(name, None):
            del self._settings[section][name]
            self.save()

    def load(self):
        if os.path.exists("./settings/settings.ini"):
            self._settings.read("./settings/settings.ini")
        else:
            self.save()

    def on_change(self) -> None:
        self._waiting = True
        if self._thread_started is False:
            t = threading.Thread(target=self.change_checker)
            self._thread_started = True
            t.start()

    def change_checker(self) -> None:
        while self._waiting:
            self._waiting = False
            time.sleep(1)
        self.save()
        self._thread_started = False

    def save(self):
        path = os.path.abspath("./settings/settings.ini")
        with open(path, "w") as settings_file:
            self._settings.write(settings_file)


settings = Settings()
