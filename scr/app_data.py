import os
import json
from scr.settings import *

class APPDATA:
    def __init__(self):
        self.appdata_path = f"{INSTALL_PATH}\\appdata.json"

        if not os.path.exists(self.appdata_path):
            with open(self.appdata_path, "w") as f:
                defaults = {
                    "version": "B-0.0.1",
                    "theme": "default",
                    "keep_servers_online": False
                }
                f.write(json.dumps(defaults, indent=4))

    def getAppData(self, key):
        with open(self.appdata_path, "r") as f:
            data = json.load(f)
        return data[key]
    
    def setAppData(self, key, value):
        with open(self.appdata_path, "r") as f:
            data = json.load(f)
        data[key] = value
        with open(self.appdata_path, "w") as f:
            f.write(json.dumps(data, indent=4))
AppData = APPDATA()