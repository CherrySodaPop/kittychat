import core.common
import core.wawalog
import core.packets
import os
import typing
import socket

KC_CLIENT_PACKET_TOO_BIG = "Attempted to send packet that was too big!"
KC_SERVER_BAD_DATA: str = "Received bad data!"

# client data
DATA_PATH = "data_c/"
SETTINGS_FILE = "settings.json"
SETTINGS_PATH = DATA_PATH + SETTINGS_FILE

# cache data
# TODO: cache room data

class client:
    def __init__(self) -> None:
        self.instance: socket.socket = None
        self.settings: dict = {}
        self.server_settings: dict = {}

    def update_settings(self) -> None:
        _info_: dict = {}
        
        if os.path.isfile(DATA_PATH):
            _read_ = open(SETTINGS_PATH, "r")
            _info_ = json.load(_read_)
            _read_.close()
        
        self.settings["address"] = _info_.get("address", "localhost")
        self.settings["port"] = _info_.get("port", core.common.DEFAULT_PORT)
    
    def start(self) -> None:
        self.instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.update_settings()

        self.instance.connect(
            (
                self.settings.get("address", "localhost"),
                self.settings.get("port", core.common.DEFAULT_PORT),
            )
        )

    def stop(self) -> None:
        self.instance = None
        self.settings = {}
        self.server_settings = {}

    def main(self) -> None:
        while self.instance:
            try:
                _message: bytes = self.instance.recv(core.packets.PACKET_SIZE_LIMIT)
            except:
                core.wawalog.log(KC_SERVER_BAD_DATA)

    def send_info(self, socket: socket.socket, data:bytes) -> None:
        if len(info) > core.packets.PACKET_SIZE_LIMIT:
            core.wawalog.log(KC_CLIENT_PACKET_TOO_BIG)
        socket.send(data)