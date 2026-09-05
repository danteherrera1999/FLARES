from daq.DaqManager import DaqManager
from gui.GuiMain import GuiMain
from data.PlotBuffer import PlotBuffer
import numpy as np
import queue


channels = []
for i in range(4):
    for j in range(16):
        channels.append(f"cDAQ1Mod{i+1}/ai{j}")
print(channels)
config={"channels":channels,
        "data queue": queue.Queue(),
        "plot buffer": PlotBuffer(),
        "analog input devices":[f"cDAQ1Mod{1+i}" for i in range(4)],
        }
config["channel map"]= {ch: i for i, ch in enumerate(config["channels"])}

my_daq_manager = DaqManager(config)

my_gui = GuiMain(config)

my_daq_manager.start()
try:
    my_gui.run()
finally:
    my_daq_manager.stop_event.set()