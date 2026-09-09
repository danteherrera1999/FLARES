import nidaqmx
from flares.daq.CompactModule import CompactModule


class DigitalInputModule(CompactModule):
    def __init__(self,DEVICE):
        super().__init__(DEVICE)
        self.io_type = "Digital Input"
        self.channels = [x.name for x in self.io[self.io_type]]