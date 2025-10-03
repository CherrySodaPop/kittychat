import core.client
import core.server
import core.wawalog
import sys

import os

sys_param = []
for i in sys.argv:
    sys_param.append(i)

if "--client" in sys_param:
    client = core.client.client()
    client.start()
    client.main()
else:
    server = core.server.server()
    server.start()
    server.main()