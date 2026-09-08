import nidaqmx



class CompactModule():
    def __init__(self,DEVICE):
        self.device = DEVICE
        self.channels = []
        self.detect_hardware()
    def detect_hardware(self):
        self.detect_channels()
        print(self.device.product_type)
        print(self.device.ai_physical_chans)
    def detect_channels(self):
        io_types = {
            "Analog Input": self.device.ai_physical_chans,
            "Analog Output": self.device.ao_physical_chans,
            "Digital Input": self.device.di_lines,
            "Digital Output": self.device.do_lines,
            "Counter Input": self.device.ci_physical_chans,
            "Counter Output": self.device.co_physical_chans,
        }
        print(io_types)


