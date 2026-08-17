from daq.AnalogTask import AnalogTask
from time import time
import numpy as np
import queue

t0 = time()
my_data_queue = queue.Queue()
my_task = AnalogTask("PXI1Slot2",my_data_queue)


my_task.start()

while time()-t0 < 1:
    try:
        data = my_data_queue.get(block=False)
        print(data)
    except queue.Empty:
        pass
my_task.stop()