from flares.daq.AnalogTask import AnalogTask
from flares.data.Packets import DataPacket
import numpy as np
import queue
import threading

class DaqManager(threading.Thread):

    def __init__(self,SYSTEM_CONFIG,daemon=True):
        super().__init__(daemon=daemon)
        self.system_config = SYSTEM_CONFIG
        self.data_queue = self.system_config["data queue"] # Processed Data Outward Queue
        self.plot_buffer = self.system_config["plot buffer"] # Lossful Buffer for Plots
        self.tasks = [] # All task objects
        self.analog_packet_queue = queue.Queue() # Raw Data Queue From Analog
        self.configure()
        self.stop_event = threading.Event()

    def configure(self):
        self.tasks.append(AnalogTask(self.system_config["analog input devices"],self.analog_packet_queue)) # Append Analog Input Task

    def run(self):

        self.start_all_tasks()

        try:
            while not self.stop_event.is_set():
                try:
                    packet = self.analog_packet_queue.get(timeout=.1)
                    
                except queue.Empty:
                    continue

                self.handle_packet(packet)
        finally:
            self.stop()

    def start_all_tasks(self):
        for task in self.tasks:
            task.start()

    def stop(self):
        for task in self.tasks:
            task.stop()

    def handle_packet(self,packet):
        new_packet = DataPacket(packet.packet_index,packet.data) #Standin for calibration
        self.plot_buffer.extend_all_buffers(new_packet)