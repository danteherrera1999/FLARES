from daq.DaqManager import DaqManager
import numpy as np
import queue
from time import time

my_data_queue = queue.Queue()
my_daq_manager = DaqManager(my_data_queue)


my_daq_manager.start()

t0 = time()

while time() - t0 < 2:
    packet = my_data_queue.get()
    print(f"Packet {packet.packet_index}, Size: {packet.data.shape}")

my_daq_manager.stop_event.set()