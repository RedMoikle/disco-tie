from enum import Enum
import json

SETTINGS_FILE = "settings.json"



class Option:
    settings_data = None
    def __init__(self, setting, color, increase_func, decrease_func, maximum=10, wrap=False):
        self.setting = setting

        self.value = 0
        self.color=color
        self.maximum=maximum
        self.wrap=wrap

        self.increase_func = increase_func
        self.decrease_func = decrease_func

        self.load_setting()

    @classmethod
    def check_settings_file(cls):
        if cls.settings_data is None:
            with open(SETTINGS_FILE, "r+") as f:
                cls.settings_data = json.load(f)
        return  cls.settings_data

    def load_setting(self):
        data = self.check_settings_file()
        self.value = data["settings"][self.setting]

    def save_setting(self):
        data = self.check_settings_file()
        data["settings"][self.setting] = self.value
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def increase(self):
        self.value += 1
        if self.maximum is not None:
            if not self.wrap:
                self.value = self.maximum
            else:
                self.value = self.value - self.maximum - 1

        self.save_setting()
        self.increase_func(self.value)

    def decrease(self):
        self.value -= 1
        if self.value < 0:
            if not self.wrap:
                self.value = 0
            elif self.maximum is None:
                raise ValueError("Cannot wrap values with no maximum")
            else:
                self.value = self.maximum + self.value - 1
        self.save_setting()
        self.decrease_func(self.value)

