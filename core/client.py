import core.packets
import socket

class client:
    def __init__(self) -> None:
        self.instance: socket.socket = None
        self.settings: dict = {}
        self.server_settings: dict = {}
    
    def start(self) -> None:
        self.instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def stop(self) -> None:
        self.instance = None

    def main(self) -> None:
        while self.instance:
            pass

    def connect_to_server(self) -> None:
        pass
