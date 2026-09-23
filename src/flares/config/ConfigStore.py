import threading
import numpy as np



class ConfigStore:

    def __init__(self,SYSTEM_CONFIG):
        self.system_config = SYSTEM_CONFIG
        self.lock = threading.Lock()
        self.n_config = -1
        self.stored_config = {}
        self.modules = SYSTEM_CONFIG["hardware config"].modules
        self.clear_config()

    def clear_config(self):
        with self.lock:
            self.stored_config = {"module info":{}}
            for module in self.modules:
                channel_info = [ChannelConfig(channel,module) for channel in module.channels]
                n = sum(np.array([module.name in name for name in self.stored_config["module info"].keys()]))
                if n ==0:
                    self.stored_config["module info"][module.name] = channel_info
                else:
                    self.stored_config["module info"][f"{module.name}_{n+1}"]=channel_info
            self.n_config += 1

    def update(self,NEW_CONFIG):
        with self.lock:
            for module,new_channel_info in NEW_CONFIG.items():
                for channelElement, new_info in zip(self.stored_config['module info'][module],new_channel_info):
                    channelElement.update(new_info)
            self.n_config += 1

    def get_n_config(self):
        with self.lock:
            return self.n_config

class ChannelConfig:

    def __init__(self,CHANNEL,MODULE):
        self.name = CHANNEL
        self.type = MODULE.ptype
        self.alias = ""
        self.group = ""
        self.enabled = False

    def update(self,NEW_INFO):
        self.group = NEW_INFO["group"]
        self.alias = NEW_INFO["alias"]
