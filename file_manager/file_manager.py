import json
import os
from typing import List, Dict, Any
from models.exception import GymException


class FileManager:

    def __init__(self, data_dir: str = "data"):
        self.__data_dir: str = data_dir
        os.makedirs(self.__data_dir, exist_ok=True)

    @property
    def data_dir(self) -> str:
        return self.__data_dir

    def _get_full_path(self, filename: str) -> str:
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        return os.path.join(self.__data_dir, filename)

    def file_exists(self, filename: str) -> bool:
        return os.path.isfile(self._get_full_path(filename))

    def load(self, filename: str) -> List[Dict[str, Any]]:
        path = self._get_full_path(filename)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, filename: str, data: List[Dict[str, Any]]) -> None:
        path = self._get_full_path(filename)
        temp_path = f"{path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            os.replace(temp_path, path)
        except (OSError, TypeError) as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise GymException(f"Failed to save data to '{filename}': {e}", 500)
