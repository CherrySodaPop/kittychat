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

_KC_PACKET_COUNT_: int = -1
def _reg_packet_id_() -> int:
    global _KC_PACKET_COUNT_
    _KC_PACKET_COUNT_ = _KC_PACKET_COUNT_ + 1
    return _KC_PACKET_COUNT_

P_CONFIRMED:tuple       = (_reg_packet_id_(), PACKET_DEF_START)
P_LOGIN:tuple           = (_reg_packet_id_(), PACKET_DEF_START + PACKET_DEF_STRING + PACKET_DEF_STRING)                     # username, password
P_REGISTER:tuple        = (_reg_packet_id_(), PACKET_DEF_START + PACKET_DEF_STRING + PACKET_DEF_STRING + PACKET_DEF_STRING) # username, password, registration password
P_MESSAGE:tuple         = (_reg_packet_id_(), PACKET_DEF_START + PACKET_DEF_STRING)                                         # message
P_SERVER_SHUTDOWN:tuple = (_reg_packet_id_(), PACKET_DEF_START)
P_DISCONNECTED:tuple    = (_reg_packet_id_(), PACKET_DEF_START)

ID_TO_PACKET = [
    P_CONFIRMED,
    P_LOGIN,
    P_REGISTER,
    P_MESSAGE,
    P_SERVER_SHUTDOWN,
    P_DISCONNECTED,
]

def make(packet: tuple, data: tuple) -> tuple:
    return (packet[PACKET_ID], pack(packet[PACKET_FORMAT], data))

def pack(packet_def: str, data: tuple) -> bytes:
    return struct.pack(packet_def, data)

def unpack(id: int, data: bytes) -> tuple:
    if id >= len(ID_TO_PACKET) or id < 0: return None
    struct.unpack(ID_TO_PACKET[id][PACKET_FORMAT], data)