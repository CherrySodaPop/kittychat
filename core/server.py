import core.wawalog
import core.packets
import os
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
KC_SERVER_BAD_DATA: str = "Received bad data!"
KC_SERVER_CONNECTION_STARTED: str = "Client has connected <%s>"
KC_SERVER_CONNECTION_END: str = "Client disconnected <%s>"
KC_SERVER_STOPPING: str = "Stopping server..."

KC_SERVER_CONSOLE_UNKNOWN_COMMAND:str = "Unknown command <%s>"

SOCKET_LISTEN_TIMEOUT: float = 0.1

CLIENT_SOCKET: int = 0
CLIENT_THREAD: int = 1
CLIENT_STOP_EVENT: int = 2

USER_ID_INVALID: int = -1
CURRENT_ROOM_INVALID: str = ""

PATH_TO_ROOM = "/data/rooms/%s"
PATH_TO_CHUNK_IN_ROOM = "/data/rooms/%s/%s"
CHUNK_FILE_EXTENSION = ".meow"

class active_client_data:
    def __init__(self) -> None:
        self.user_id = USER_ID_INVALID
        self.current_room = CURRENT_ROOM_INVALID

class server:
    def __init__(self) -> None:
        self.instance: socket.socket = None
        self.connection_request_thread: threading.Thread = None
        self.settings: dict = {}

        self.clients: array = [] # (socket, thread, stop_event, active_client_data)
        self.active_chunks: dict = {} # the current chunk of messages, will be saved after a threshold of messages are sent and the chunk reset

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
                _active_client_data_ = active_client_data()
                _e_ = threading.Event()
                _t_ = threading.Thread(target=self.user_thread, args=[_e_, _socket_, _address_, _active_client_data_])
                _t_.start()
                _client_ = (_socket_, _t_, _e_, _active_client_data_)
                self.clients.append(_client_)

                core.wawalog.log(KC_SERVER_CONNECTION_STARTED % _socket_)
            except:
                pass
    
    def user_thread(self, event: threading.Event, socket: socket.socket, address:str, cli_data:active_client_data) -> None:
        while not event.is_set():
            try:
                _m_: tuple = socket.recv(core.packets.PACKET_SIZE_LIMIT)
                _id_: int = _message_[core.packets.PACKET_ID]
                _b_data_: bytes = _message_[core.packets.PACKET_BYTE_DATA]
                _data_: tuple = core.packets.unpack(_id_, _b_data_)
                self.handle_incoming_data(socket, cli_data, _id_, _data_)
            except:
                core.wawalog.log(KC_SERVER_BAD_DATA)
     
    def disconnect_client(self, client: tuple) -> None:
       client[CLIENT_SOCKET].close()
       client[CLIENT_STOP_EVENT].set()
       self.clients.remove(client)
    
    def send_info(self, socket: socket.socket, data:bytes) -> None:
        if len(info) > core.packets.PACKET_SIZE_LIMIT:
            core.wawalog.log(KC_SERVER_PACKET_TOO_BIG)
            return
        socket.send(data)
    
    def handle_incoming_data(self, socket: socket.socket, cli_data: active_client_data, id: int, data: tuple) -> None:
        match id:
            case core.packets.P_ID_CONFIRMED:
                pass
            case core.packets.P_ID_LOGIN:
                pass
            case core.packets.P_ID_REGISTER:
                pass
            case core.packets.P_ID_MESSAGE:
                message_read(cli_data, data)
            case core.packets.P_GOTO_ROOM:
                pass
            case _:
                pass
        pass

    # ========== Incoming Data Cases ==========

    def message_read(self, cli_data:active_client_data, data: tuple) -> None:
        # user is not logged in!
        if cli_data.user_id == USER_ID_INVALID: return
        # user is not in a valid room!
        if cli_data.current_room == CURRENT_ROOM_INVALID: return
        if not self.active_chunks.has(cli_data.current_room): return
    
    # =========================================

    def make_active_chunk(self, room_name: str) -> dict:
        return
        {
            room_name :
            {
                "messages" :
                [
                    ### EXAMPLE MESSAGE ###
                    #{
                        #"user" :
                        #"date" :
                    #}
                ]
            }
        }
    
    #def make_message(self, room_name: str, cli )
    
    def save_active_chunk(self, room_name: str) -> None:
        if not self.active_chunks.has(room_name): return

        _chunk_file_name_ = str(self.get_current_chunk_index()) + CHUNK_FILE_EXTENSION
        _chunk_path_ = PATH_TO_CHUNK_IN_ROOM % [room_name, _chunk_file_name_]
        _chunk_file_ = open(_chunk_path_, "w")

        _chunk_file_.write(json.dumps(self.active_chunks[room_name]))

        _chunk_file_.close()

    def get_current_chunk_index(self, room_name: str) -> int:
        _room_path_ = PATH_TO_ROOM % [room_name]

        # no data for this room exists yet, which means its a brand new chunk
        if not os.path.isdir(room_path): return 0

        _chunk_index_ = 0

        for i in os.scandir(room_path):
            if not i.name.endswith(".meow"): continue
            _chunk_index_ += 1

        return _chunk_index_