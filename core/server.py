import core.wawalog
import core.packets
import os
import typing
import socket
import json
import threading
import sys
import time
import hashlib
import array

KC_SERVER_STARTING: str = "Kitty Chat server %s is starting!"
KC_SERVER_INFO: str = "Hosting: %s, %s"
KC_SERVER_START: str = "Server started..."
KC_SERVER_FAIL: str = "Server failed to start!"
KC_SERVER_BEGINNING_CONNECTION_ACCEPTING: str = "Begining to accept connections..."
KC_SERVER_PACKET_TOO_BIG: str = "Attempted to send packet that was too big!"
KC_SERVER_BAD_DATA: str = "Received bad data!"
KC_SERVER_CONNECTION_STARTED: str = "Client has connected <%s>"
KC_SERVER_CONNECTION_END: str = "Client disconnected <%s>"
KC_SERVER_STOPPING: str = "Stopping server..."

KC_VERSION: str = "0.0.1-dev" # both for display and version checking

KC_SERVER_CONSOLE_UNKNOWN_COMMAND:str = "Unknown command <%s>"

SOCKET_LISTEN_TIMEOUT: float = 0.1

CLIENT_SOCKET: int = 0
CLIENT_THREAD: int = 1
CLIENT_STOP_EVENT: int = 2

USER_ID_INVALID: int = -1
CURRENT_ROOM_INVALID: str = ""

DEFAULT_PORT:int = 6666
DEFAULT_REGISTER_PASS:str = "meow_pleasechangeme_meow"
DEFAULT_CHUNK_SIZE:int = 256
DEFAULT_MAX_CONNECTIONS:int = 256

MAX_CHARACTER_LENGTH:int = 18

# room data
PATH_TO_ROOM = "data/rooms/%s/"
PATH_TO_ROOM_SETTINGS = "settings.json"
PATH_TO_ROOM_CHUNKS = "data/rooms/%s/chunks/"
CHUNK_FILE_EXTENSION = ".meow"
NO_CHUNK_DATA = ["no_chunk_data"]

# server data
DATA_PATH = "data/"
SETTINGS_FILE = "settings.json"
USERS_FILE = "users.json"
SETTINGS_PATH = DATA_PATH + SETTINGS_FILE
USERS_PATH = DATA_PATH + USERS_FILE

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
        self.rooms: dict = {} # the current chunk of messages, will be saved after a threshold of messages are sent and the chunk reset

    def update_settings(self) -> None:
        _info_: dict = {}
        
        if os.path.isdir(DATA_PATH):
            _read_ = open(SETTINGS_PATH, "r")
            _info_ = json.load(_read_)
            _read_.close()

        self.settings["server_name"] = _info_.get("server_name", "My Kitty Chat Server")
        self.settings["account_registration"] = _info_.get("account_registration", False)
        self.settings["account_registration_password"] = _info_.get("account_registration_password", DEFAULT_REGISTER_PASS) # TODO: make it use a random default password
        self.settings["address"] = _info_.get("address", "localhost")
        self.settings["port"] = _info_.get("port", DEFAULT_PORT) # i did want 666 as a port as a reference to doom and funny satanic number but it requires admin perms for ports that low...
        self.settings["max_connections"] = _info_.get("max_connections", DEFAULT_MAX_CONNECTIONS)
        self.settings["chunk_size"] = _info_.get("chunk_size", DEFAULT_CHUNK_SIZE)

    def save_server_settings(self) -> None:
        self.save_file("data/", "settings.json", self.settings)

    def start(self) -> None:
        core.wawalog.log(KC_SERVER_STARTING % KC_VERSION)

        self.update_settings()

        core.wawalog.log(KC_SERVER_INFO % (self.settings["server_name"], "%s:%s" % (self.settings["address"], self.settings["port"]) ))

        self.instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.instance.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.instance.settimeout(SOCKET_LISTEN_TIMEOUT)

        try:
            self.instance.bind((self.settings["address"], self.settings["port"]))
            self.instance.listen(self.settings["max_connections"])
            core.wawalog.log(KC_SERVER_START)
        except:
            core.wawalog.error(KC_SERVER_FAIL)
            sys.exit()

    def stop(self) -> None:
        core.wawalog.log(KC_SERVER_STOPPING)
        
        self.save_server_settings()
        self.save_rooms()

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
                # wait for data
                _message_: bytes = socket.recv(core.packets.PACKET_SIZE_LIMIT)
                # get the packet id
                _id_: int = struct.unpack(packets.PACKET_DEF_START, _message_[0:packets.PACKET_DEF_IDSIZE_BITS])
                _b_data: bytes = _message_[packets.PACKET_DEF_IDSIZE_BITS:len(_message_)]

                # we got the packet id type, now unpack it
                _data_: tuple = core.packets.unpack(_id_, _b_data_)

                self.handle_incoming_data(socket, cli_data, _id_, _data_)
            except:
                core.wawalog.log(KC_SERVER_BAD_DATA)
                # TODO: consider a ban system for sending bad data
     
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
                self.incoming_data_handle_login(cli_data, data[0], data[1])
            case core.packets.P_ID_REGISTER:
                self.register_user(data[0], data[1], data[2])
            case core.packets.P_ID_MESSAGE:
                self.incoming_data_handle_message(cli_data, data[0])
            case core.packets.P_GOTO_ROOM:
                pass
            case _:
                pass
        pass

    # ========== Incoming Data Cases ==========

    def incoming_data_handle_login(self, cli_data:active_client_data, username:str, password_hashed:str) -> None:
        # already logged in
        if cli_data.user_id != USER_ID_INVALID: return
        
        # wrong credentials
        if not self.are_user_credentials_correct(username, password_hashed): return

    def incoming_data_handle_message(self, cli_data:active_client_data, message: str) -> None:
        # user is not logged in!
        if cli_data.user_id == USER_ID_INVALID: return

        _target_room_: str = cli_data.current_room

        # user is not in a valid room!
        if _target_room_ == CURRENT_ROOM_INVALID: return
        if not self.rooms.has(_target_room_): return

        # this room is missing the messages portion???
        #if not self.room[_target_room_].has("messages"): return

        _message_data_ = {
            "user" : cli_data.user_id,
            "time" : time.time_ns(),
            "message" : message,
            "is_encrypted" : False,
        }
        self.rooms[_target_room_]["messages"].append(_message_data_)

        # chunk size has been reached, save the chunk to disk
        if self.rooms[_target_room_]["messages"].size() > self.settings.get("chunk_size", DEFAULT_CHUNK_SIZE):
            self.save_active_chunk(i, self.get_current_chunk_index(i))

    # ========== Outgoing Data Cases ==========

    def outgoing_data_send_chunk_info(self, socket: socket.socket, room: str, chunk: int) -> None:
        if socket == None: return
        
        _chunk_: dict = get_chunk_data(room, chunk)
        if _chunk_ == NO_CHUNK_DATA: return

        self.send_info(socket, packets.make(packets.P_CHUNK_INFO,
                (
                    room,
                    chunk,
                    json.dumps(_chunk_))
            )
        )
    
    def outgoing_data_send_server_settings(self, socket: socket.socket) -> None:
        if socket == None: return

        self.send_info(socket, packets.make(packets.P_SERVER_SETTINGS,
                (
                    self.settings.get("server_name", "My Kitty Chat Server"),
                    self.settings.get("account_registration", False)
                )
            )
        )

    # =========================================

    def register_user(self, username: str, password_hashed: str, register_pass_hashed: str) -> bool:
        if self.settings.get("account_registration", False): return

        if (len(username) > MAX_CHARACTER_LENGTH or
            len(password_hashed) != 128 or
            len(register_pass_hashed) != 128):
            return
        
        _register_pass_string_: str = self.settings.get("account_registration_password", DEFAULT_REGISTER_PASS)
        _register_pass_hash_: str = hashlib.sha512(_register_pass_string_.encode()).hexdigest()
        if _register_pass_hash_ != register_pass_hashed: return 

        _user_data_: dict = self.get_all_user_data()

        _user_data_[username] = {
            "password_hashed" : password_hashed,
        }

        self.save_file(DATA_PATH, USERS_FILE, _user_data_)
    
    def are_user_credentials_correct(self, username: str, password_hashed: str) -> bool:
        if len(username) > MAX_CHARACTER_LENGTH or len(password_hashed) != 128: return False

        _user_data_: dict = self.get_all_user_data()

        if not _user_data_.has(username): return False
        
        return _user_data_[username]["password_hashed"] == password_hashed

    def get_all_user_data(self) -> dict:
        _user_data_: dict = {}
        if os.path.isfile(USERS_PATH):
            _user_data_file_ = open(USERS_PATH, "r")
            _user_data_string_data_:str = _chunk_file_.read()
            _user_data_file_.close()
            _user_data_ = json.loads(_user_data_string_data_)
        return _user_data_

    def create_room(self, room_name: str) -> None:
        if self.rooms.has(room_name): return

        _room_ = {
            "messages" : [],
            "settings" : {}
        }

        self.rooms[room_name] = _room_

    def save_rooms(self) -> None:
        for i in self.rooms.keys():
            self.save_active_chunk(i, self.get_current_chunk_index(i))
            self.save_room_settings()

    def save_room_settings(self, room_name: str) -> None:
        self.save_file(PATH_TO_ROOM % room_name, PATH_TO_ROOM_SETTINGS, self.rooms[room_name]["settings"])

    def get_chunk_data(self, room_name: str, chunk: int) -> array:
        # check active chunk
        if self.rooms.has(room_name) and self.get_current_chunk_index(room_name) == chunk:
            return self.rooms[room_name]["messages"]

        # no active chunk found, check disk
        _chunk_file_name_ = str(chunk) + CHUNK_FILE_EXTENSION
        _chunk_path_ = (PATH_TO_ROOM_CHUNKS % room_name) + _chunk_file_name_

        if not os.path.isfile(_chunk_path_): return NO_CHUNK_DATA
        
        _chunk_file_ = open(_chunk_path_, "r")
        _string_data_ = _chunk_file_.read()
        _chunk_file_.close()

        _data_ = json.loads(str(_string_data_))

        if type(_data_) is not array: return NO_CHUNK_DATA

        return _data_

    def save_active_chunk(self, room_name: str) -> None:
        if not self.rooms.has(room_name): return

        _chunks_path_ = PATH_TO_ROOM_CHUNKS % room_name
        _chunk_file_name_ = str(self.get_current_chunk_index()) + CHUNK_FILE_EXTENSION
        _chunk_file_path_ = _chunks_path_ + _chunk_file_name_

        self.save_file(_chunks_path_, _chunk_file_path_, self.rooms[room_name]["messages"])
        self.rooms[room_name]["messages"] = []

    def get_current_chunk_index(self, room_name: str) -> int:
        _room_path_ = PATH_TO_ROOM % [room_name]

        # no data for this room exists yet, which means its a brand new chunk
        if not os.path.isdir(room_path): return 0

        _chunk_index_ = 0

        for i in os.scandir(room_path):
            if not i.name.endswith(".meow"): continue
            _chunk_index_ += 1

        return _chunk_index_
    
    def save_file(self, dir:str, file:str, data:dict) -> None:
        os.makedirs(dir, exist_ok=True)

        _file_ = open(dir + file, "w")
        _file_.write(json.dumps(data, indent=4))
        _file_.close()