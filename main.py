import core.server
import core.wawalog
import sys

sys_param = []
for i in sys.argv:
    sys_param.append(i)

KC_SERVER_START:str = "Starting Kitty Chat %s!"
KC_END:str = "Ending Kitty Chat..."
KC_VERSION: str = "0.0.1-dev"
KC_SETTINGS_PATH: str = "data/settings.json"

if "--client" in sys_param:
    pass
else:
    core.wawalog.log(KC_SERVER_START % KC_VERSION)

    server = core.server.server()
    server.start(KC_SETTINGS_PATH)
    server.main()

    core.wawalog.log(KC_END)
    server.stop()
