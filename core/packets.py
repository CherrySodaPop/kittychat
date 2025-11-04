import struct
import typing

CHARACTER_LIMIT: int = 1024

PACKET_ID: int = 0
PACKET_FORMAT: int = 1
PACKET_BYTE_DATA:int = 1

PACKET_DEF_ENDIAN: str = ">"
PACKET_DEF_IDSIZE: str = "B" # 0-255
PACKET_DEF_IDSIZE_BITS: int = 8 # 0-255
PACKET_DEF_START: str = PACKET_DEF_ENDIAN + PACKET_DEF_IDSIZE
PACKET_DEF_BOOL: str = "?"
PACKET_DEF_UNSIGNED_INT: str = "I"
PACKED_DEF_SIGNED_INT: str = "i"
PACKET_DEF_STRING: str = CHARACTER_LIMIT * "cccc"
PACKET_SIZE_LIMIT: int = (CHARACTER_LIMIT * 4) + 8 # 4104 bytes

###### PACKET DEF START ######

P_ID_CONFIRMED: int = 0
P_CONFIRMED: tuple = (P_ID_CONFIRMED, PACKET_DEF_START)

P_ID_LOGIN: int = 1
P_LOGIN: tuple = (P_ID_LOGIN, PACKET_DEF_START +
    PACKET_DEF_STRING + # username
    PACKET_DEF_STRING # password hashed
)

P_ID_REGISTER: int = 2
P_REGISTER: tuple = (P_ID_REGISTER, PACKET_DEF_START +
    PACKET_DEF_STRING + # username
    PACKET_DEF_STRING + # password hashed
    PACKET_DEF_STRING # registration password hashed
)

P_ID_SERVER_SHUTDOWN: int = 3
P_SERVER_SHUTDOWN: tuple = (P_ID_SERVER_SHUTDOWN, PACKET_DEF_START)

P_ID_DISCONNECTED: int = 4
P_DISCONNECTED: tuple = (P_ID_DISCONNECTED, PACKET_DEF_START)

P_ID_MESSAGE: int = 5
P_MESSAGE: tuple = (P_ID_MESSAGE, PACKET_DEF_START +
    PACKET_DEF_STRING # message
)

P_ID_GOTO_ROOM: int = 6
P_GOTO_ROOM: tuple = (P_ID_GOTO_ROOM, PACKET_DEF_START +
    PACKET_DEF_STRING # room
)

P_ID_CHUNK_INFO_REQUEST: int = 7
P_CHUNK_INFO_REQUEST: tuple = (P_ID_CHUNK_INFO_REQUEST, PACKET_DEF_START +
    PACKET_DEF_STRING + # room
    PACKET_DEF_UNSIGNED_INT # chunk id
)

P_ID_CHUNK_INFO: int = 8
P_CHUNK_INFO: tuple = (P_ID_CHUNK_INFO, PACKET_DEF_START +
    PACKET_DEF_STRING + # room
    PACKET_DEF_UNSIGNED_INT + # chunk id
    PACKET_DEF_STRING # data
)

P_ID_CREATE_ROOM: int = 9
P_CREATE_ROOM: tuple = (P_ID_CREATE_ROOM, PACKET_DEF_START +
    PACKET_DEF_STRING # room
)

P_ID_SERVER_SETTINGS_REQUEST: int = 10
P_SERVER_SETTINGS_REQUEST: tuple = (P_ID_SERVER_SETTINGS_REQUEST, PACKET_DEF_START)

P_ID_SERVER_SETTINGS:int = 11
P_SERVER_SETTINGS: tuple = (P_ID_SERVER_SETTINGS, PACKET_DEF_START +
    PACKET_DEF_STRING + # server_name
    PACKET_DEF_BOOL # account_registration
)

ID_TO_PACKET = [
    P_CONFIRMED,
    P_LOGIN,
    P_REGISTER,
    P_SERVER_SHUTDOWN,
    P_DISCONNECTED,
    P_MESSAGE,
    P_GOTO_ROOM,
    P_CHUNK_INFO_REQUEST,
    P_CHUNK_INFO,
    P_CREATE_ROOM,
    P_SERVER_SETTINGS_REQUEST,
    P_SERVER_SETTINGS,
]

###### PACKET DEF END ######

def make(packet: tuple, data: tuple) -> tuple:
    return (packet[PACKET_ID], pack(packet[PACKET_FORMAT], data))

def pack(packet_def: str, data: tuple) -> bytes:
    return struct.pack(packet_def, data)

def unpack(id: int, data: bytes) -> tuple:
    if id >= len(ID_TO_PACKET) or id < 0: return None
    struct.unpack(ID_TO_PACKET[id][PACKET_FORMAT], data)