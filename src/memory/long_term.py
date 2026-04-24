import json
import os
from typing import Any


class LongTermMemory:
    def __init__(self, path: str = "data/profile.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write({})

    def _read(self) -> dict:
        with open(self.path) as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        with open(self.path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, key: str, value: Any) -> None:
        data = self._read()
        data[key] = value
        self._write(data)

    def retrieve(self, key: str) -> Any:
        return self._read().get(key)

    def all(self) -> dict:
        return self._read()
