import nidaqmx
from abc import ABC,abstractmethod

class CompactModule(ABC):
    def __init__(self,DEVICE):
        self.device = DEVICE
        self.ptype = DEVICE.product_type
        self.detect_hardware()

    def detect_hardware(self):
        self.io = {
            "Analog Input": self.device.ai_physical_chans,
            "Analog Output": self.device.ao_physical_chans,
            "Digital Input": self.device.di_lines,
            "Digital Output": self.device.do_lines,
            "Counter Input": self.device.ci_physical_chans,
            "Counter Output": self.device.co_physical_chans,
        }
        
    @classmethod
    def create(cls,DEVICE):
        from flares.daq.supported_modules.AnalogInputModule import AnalogInputModule
        from flares.daq.supported_modules.DigitalInputModule import DigitalInputModule
        from flares.daq.supported_modules.DigitalOutputModule import DigitalOutputModule
        module_support = {
            "Analog Input": ["9202"],
            "Digital Input": ["9425"],
            "Digital Output": ["9401","9476"]
        }
        device_product_type = DEVICE.product_type
        device_type = None
        for key,val in module_support.items():
            if any([x in device_product_type for x in val]):
                device_type = key

        match device_type:
            case "Analog Input":
                return AnalogInputModule(DEVICE)
            case "Digital Input":
                return DigitalInputModule(DEVICE)
            case "Digital Output":
                return DigitalOutputModule(DEVICE)

