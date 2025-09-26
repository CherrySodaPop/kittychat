import core.server
import core.wawalog
import sys

import os

sys_param = []
for i in sys.argv:
    sys_param.append(i)

if "--client" in sys_param:
    pass
else:
    server = core.server.server()
    server.start()
    server.main()