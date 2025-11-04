import os
import json
import typing

VERSION: str = "0.0.1-dev" # both for display and version checking

DEFAULT_PORT: int = 6666

MAX_USERNAME_LENGTH: int = 18

def save_file(dir:str, file:str, data:dict) -> None:
    os.makedirs(dir, exist_ok=True)
    _file_ = open(dir + file, "w")
    _file_.write(json.dumps(data, indent=4))
    _file_.close()