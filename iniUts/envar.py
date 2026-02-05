from typing import Optional
import os


class Envar:
    def __init__(self, key: str, default: Optional[str] = None):
        self.key = key
        self.default = default

    def get_value(self):
        if self.default is not None:
            return os.getenv(self.key, self.default)
        else:
            value = os.getenv(self.key)
            if not value:
                raise Exception(f"envar '{self.key}' not found!")
            return value
