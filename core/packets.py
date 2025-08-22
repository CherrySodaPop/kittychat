import struct

KC_CHARACTER_LIMIT: int = 1000

KC_PACKET_DEF_ENDIAN: str = ">"
KC_PACKET_DEF_IDSIZE: str = "B" # 0-255
KC_PACKET_DEF_START: str = KC_PACKET_DEF_ENDIAN + KC_PACKET_DEF_IDSIZE
KC_PACKET_DEF_STRING: str = KC_CHARACTER_LIMIT * "cccc"

_KC_PACKET_COUNT_: int = -1

KC_PACKET_CONFIRMED:tuple = (_reg_packet_id_(), KC_PACKET_DEF_START)
KC_PACKET_LOGIN:tuple     = (_reg_packet_id_(), KC_PACKET_DEF_START + KC_PACKET_DEF_STRING + KC_PACKET_DEF_STRING)                        # username, password
KC_PACKET_REGISTER:tuple  = (_reg_packet_id_(), KC_PACKET_DEF_START + KC_PACKET_DEF_STRING + KC_PACKET_DEF_STRING + KC_PACKET_DEF_STRING) # username, password, registration password
KC_PACKET_MESSAGE:tuple   = (_reg_packet_id_(), KC_PACKET_DEF_START + KC_PACKET_DEF_STRING) # message

def pack(packet: tuple) -> bytes:                                     return struct.pack(packet[1], packet[0])
def pack(packet: tuple, data0: Any) -> bytes:                         return struct.pack(packet[1], packet[0], data0)
def pack(packet: tuple, data0: Any, data1: Any) -> bytes:             return struct.pack(packet[1], packet[0], data0, data1)
def pack(packet: tuple, data0: Any, data1: Any, data2: Any) -> bytes: return struct.pack(packet[1], packet[0], data0, data1, data2)

def _reg_packet_id_() -> int:
    _KC_PACKET_COUNT_ = _KC_PACKET_COUNT_ + 1
    return _KC_PACKET_COUNT_