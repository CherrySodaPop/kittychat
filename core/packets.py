import struct
import typing

CHARACTER_LIMIT: int = 1024

PACKET_ID: int = 0
PACKET_FORMAT: int = 1
PACKET_BYTE_DATA:int = 1

PACKET_DEF_ENDIAN: str = ">"
PACKET_DEF_IDSIZE: str = "B" # 0-255
PACKET_DEF_START: str = PACKET_DEF_ENDIAN + PACKET_DEF_IDSIZE
PACKET_DEF_STRING: str = CHARACTER_LIMIT * "cccc"
PACKET_SIZE_LIMIT: int = (CHARACTER_LIMIT * 4) + 8 # 4104 bytes

###### PACKET DEF START ######

P_ID_CONFIRMED: int = 0
P_CONFIRMED: tuple = (P_ID_CONFIRMED, PACKET_DEF_START + PACKET_DEF_STRING)

P_ID_LOGIN: int = 1
P_LOGIN: tuple = (P_ID_LOGIN, PACKET_DEF_START + PACKET_DEF_STRING + PACKET_DEF_STRING) # username, password

P_ID_REGISTER: int = 2
P_REGISTER: tuple = (P_ID_REGISTER, PACKET_DEF_START + PACKET_DEF_STRING + PACKET_DEF_STRING + PACKET_DEF_STRING) # username, password, registration password

P_ID_SERVER_SHUTDOWN: int = 3
P_SERVER_SHUTDOWN: tuple = (P_ID_SERVER_SHUTDOWN, PACKET_DEF_START)

P_ID_DISCONNECTED: int = 4
P_DISCONNECTED: tuple = (P_ID_DISCONNECTED, PACKET_DEF_START)

P_ID_MESSAGE: int = 5
P_MESSAGE: tuple = (P_ID_MESSAGE, PACKET_DEF_START + PACKET_DEF_STRING)

P_ID_GOTO_ROOM: int = 6
P_GOTO_ROOM: tuple = (P_ID_GOTO_ROOM, PACKET_DEF_START + PACKET_DEF_STRING)

ID_TO_PACKET = [
    P_CONFIRMED,
    P_LOGIN,
    P_REGISTER,
    P_SERVER_SHUTDOWN,
    P_DISCONNECTED,
    P_MESSAGE,
    P_GOTO_ROOM,
]

###### PACKET DEF END ######

def make(packet: tuple, data: tuple) -> tuple:
    return (packet[PACKET_ID], pack(packet[PACKET_FORMAT], data))

def pack(packet_def: str, data: tuple) -> bytes:
    return struct.pack(packet_def, data)

def unpack(id: int, data: bytes) -> tuple:
    if id >= len(ID_TO_PACKET) or id < 0: return None
    struct.unpack(ID_TO_PACKET[id][PACKET_FORMAT], data)