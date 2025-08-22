import core.wawalog
import typing
import socket
import json
import threading
import sys

KC_SERVER_INFO: str = "Hosting: %s, %s"
KC_SERVER_START: str = "Server started..."
KC_SERVER_FAIL: str = "Server failed to start!"
KC_SERVER_BEGINNING_CONNECTION_ACCEPTING: str = "Begining to accept connections..."

class server:
    def __init__(self) -> None:
        self.instance: socket.socket = None
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

        try:
            self.instance.bind((self.settings["address"], self.settings["port"]))
            self.instance.listen(self.settings["max_connected_users"])
            core.wawalog.log(KC_SERVER_START)
        except:
            core.wawalog.error(KC_SERVER_FAIL)
            sys.exit()

    def stop(self) -> None:
        if self.instance == None: return
        self.instance.close()

    def main(self) -> None:
        _t_ = threading.Thread(target=self.listen_for_connection_request, args=())
        _t_.start()

        while True:
            pass

    def listen_for_connection_request(self) -> None:
        core.wawalog.log(KC_SERVER_BEGINNING_CONNECTION_ACCEPTING)
        while True:
            _connection_, _address_ = self.instance.accept()

    def user_thread(self) -> None:
        while True:
            pass