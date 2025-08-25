import core.wawalog
import core.packets
import typing
import socket
import json
import threading
import sys
import time
from getpass import getpass

KC_SERVER_INFO: str = "Hosting: %s, %s"
KC_SERVER_START: str = "Server started..."
KC_SERVER_FAIL: str = "Server failed to start!"
KC_SERVER_BEGINNING_CONNECTION_ACCEPTING: str = "Begining to accept connections..."
KC_SERVER_PACKET_TOO_BIG: str = "Attempted to send packet that was too big!"
KC_SERVER_CONNECTION_STARTED: str = "Client has connected <%s>"
KC_SERVER_CONNECTION_END: str = "Client disconnected <%s>"
KC_SERVER_STOPPING: str = "Stopping server..."

KC_SERVER_CONSOLE_UNKNOWN_COMMAND:str = "Unknown command <%s>"

SOCKET_LISTEN_TIMEOUT: float = 0.1

CLIENT_SOCKET:int = 0
CLIENT_THREAD:int = 1
CLIENT_STOP_EVENT:int = 2

class server:
    def __init__(self) -> None:
        self.instance: socket.socket = None
        self.connection_request_thread: threading.Thread = None
        self.clients: array = [] # (socket, thread, stop_event)
        self.settings: dict = {}

    def update_server_settings(self, settings_path: str) -> None:
        _read_ = open(settings_path, "r")
        _info_: dict = json.load(_read_)

        self.settings["server_name"] = _info_.get("server_name", "My Kitty Chat Server")
        self.settings["account_registration"] = _info_.get("account_registration", False)
        self.settings["account_registration_password"] = _info_.get("account_registration_password", "meow_pleasechangeme_meow")
        self.settings["address"] = _info_.get("address", "localhost")
        self.settings["port"] = _info_.get("port", 6666) # i did want 666 as a port as a reference to doom and funny satanic number but it requires admin perms for ports that low...
        self.settings["max_connected_users"] = _info_.get("max_connected_users", 256)

    def start(self, settings_path: str) -> None:
        self.update_server_settings(settings_path)

        core.wawalog.log(KC_SERVER_INFO % (self.settings["server_name"], "%s:%s" % (self.settings["address"], self.settings["port"]) ))

        self.instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.instance.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.instance.settimeout(SOCKET_LISTEN_TIMEOUT)

        try:
            self.instance.bind((self.settings["address"], self.settings["port"]))
            self.instance.listen(self.settings["max_connected_users"])
            core.wawalog.log(KC_SERVER_START)
        except:
            core.wawalog.error(KC_SERVER_FAIL)
            sys.exit()

    def stop(self) -> None:
        core.wawalog.log(KC_SERVER_STOPPING)
        for i in self.clients:
            self.disconnect_client(i)
        if self.instance:
            self.instance.close()
            self.instance = None

    def main(self) -> None:
        self.connection_request_thread = threading.Thread(target=self.check_for_connection_request, args=[])
        self.connection_request_thread.start()

        self.console()
    
    def console(self) -> None:
        while self.instance:
            _input_: str = input(">")
            _inputs_: array = _input_.split(" ")
            
            match _input_:
                case "stop":
                    self.stop()
                case _:
                    core.wawalog.log(KC_SERVER_CONSOLE_UNKNOWN_COMMAND % _input_)

    def check_for_connection_request(self) -> None:
        core.wawalog.log(KC_SERVER_BEGINNING_CONNECTION_ACCEPTING)
        while self.instance:
            try:
                # wait for connection
                _socket_, _address_ = self.instance.accept()

                # got one
                _e_ = threading.Event()
                _t_ = threading.Thread(target=self.user_thread, args=[_e_, _socket_, _address_])
                _t_.start()
                self.clients.append()

                core.wawalog.log(KC_SERVER_CONNECTION_STARTED)
            except:
                pass
    
    def user_thread(self, event: threading.Event, socket: socket.socket, address:str) -> None:
        while not event.is_set():
            try:
                _m_: tuple = socket.recv(core.packets.PACKET_SIZE_LIMIT)
                _id_: int = _message_[core.packets.PACKET_ID]
                _b_data_: bytes = _message_[core.packets.PACKET_BYTE_DATA]
                _data_: tuple = core.packets.unpack(_id_, _b_data_)
            except:
                pass
    
    def disconnect_client(self, client: tuple) -> None:
       client[CLIENT_SOCKET].close()
       client[CLIENT_STOP_EVENT].set()
       self.clients.remove(client)
    
    def send_info(self, client_socket: socket.socket, data:bytes) -> None:
        if len(info) > core.packets.PACKET_SIZE_LIMIT:
            core.wawalog.log(KC_SERVER_PACKET_TOO_BIG)
            return
        client_socket.send(data)