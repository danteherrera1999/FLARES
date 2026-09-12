import nidaqmx
from flares.daq.CompactModule import CompactModule

class HardwareConfig():
    def __init__(self):
        self.modules = [CompactModule.create(module) for module in nidaqmx.system.System.local().devices[1:]]
        self.all_channels = self.get_all_hardware_channels()

    def get_all_hardware_channels(self):
        if len(self.modules) >= 0:
            channels = {}
            for module in self.modules:
                if module.io_type not in channels.keys():
                    channels[module.io_type] = module.channels
                else:
                    channels[module.io_type] += module.channels
        return channels