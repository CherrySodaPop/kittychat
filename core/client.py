import core.packets
import socket

class client:
    def __init__(self) -> None:
        self.instance: socket.socket = None
        self.settings: dict = {}
        self.server_settings: dict = {}

    def connect_to_server(self) -> None:
        pass