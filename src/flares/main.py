from daq.DaqManager import DaqManager
from gui.GuiMain import GuiMain
from data.PlotBuffer import PlotBuffer
import nidaqmx
import numpy as np
import queue

config={
    "channels":DaqManager.get_hardware_channels(),
        "data queue": queue.Queue(),
        "plot buffer": PlotBuffer(),
        }
config["channel map"]= {ch: i for i, ch in enumerate(config["channels"]["Analog Input"])}

my_daq_manager = DaqManager(config)

my_gui = GuiMain(config)

my_daq_manager.start()
try:
    my_gui.run()
finally:
    my_daq_manager.stop_event.set()