import nidaqmx
from flares.daq.CompactModule import CompactModule


class AnalogInputModule(CompactModule):
    def __init__(self,DEVICE):
        super().__init__(DEVICE)
        self.io_type = "Analog Input"
        self.channels = [x.name for x in self.io[self.io_type]]