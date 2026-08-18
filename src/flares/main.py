from daq.DaqManager import DaqManager
from gui.GuiMain import GuiMain
from data.DataBuffer import DataBuffer
import numpy as np
import queue

my_data_queue = queue.Queue()
my_data_buffer = DataBuffer(1000,64)
my_daq_manager = DaqManager(my_data_queue,my_data_buffer)

my_gui = GuiMain(my_data_buffer)

my_daq_manager.start()
try:
    my_gui.run()
finally:
    my_daq_manager.stop_event.set()