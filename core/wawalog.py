import typing
import time
import colorsys
import sys
from array import array

sys_param = []
for i in sys.argv:
    sys_param.append(i)

WAWA_LOG_SIMPLE = "[WawaLog] [%s] %s"
WAWA_LOG_WARNING = "[WawaLog] [WARNING] [%s] %s"
WAWA_LOG_ERROR = "[WawaLog] [ERROR] [%s] %s"

def log(string: str) -> None:
    print(WAWA_LOG_SIMPLE % (time_formated(), string))

def warn(string: str) -> None:
    print(WAWA_LOG_WARNING % (time_formated(), string))

def error(string: str) -> None:
    print(WAWA_LOG_ERROR % (time_formated(), string))

def time_formated() -> str:
    _time_ = time.localtime()
    return "%s:%s:%s" % (_time_.tm_hour, _time_.tm_min, _time_.tm_sec)