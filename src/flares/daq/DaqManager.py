from flares.daq.AnalogTask import AnalogTask
from flares.data.Packets import DataPacket
from flares.daq.CompactModule import CompactModule
import numpy as np
import nidaqmx
import queue
import threading


class DaqManager(threading.Thread):

    def __init__(self,SYSTEM_CONFIG,daemon=True):
        super().__init__(daemon=daemon)
        self.system_config = SYSTEM_CONFIG
        self.channels = SYSTEM_CONFIG["channels"]
        self.data_queue = self.system_config["data queue"] # Processed Data Outward Queue
        self.plot_buffer = self.system_config["plot buffer"] # Lossful Buffer for Plots
        self.tasks = [] # All task objects
        self.analog_packet_queue = queue.Queue() # Raw Data Queue From Analog
        self.configure()
        self.stop_event = threading.Event()

    def configure(self):
        self.tasks.append(AnalogTask(self.channels["Analog Input"],self.analog_packet_queue)) # Append Analog Input Task

    @classmethod
    def get_hardware_channels(cls):
        modules = nidaqmx.system.System.local().devices[1:]
        if len(modules) >= 0:
            modules = [CompactModule.create(module) for module in modules]
            channels = {}
            for module in modules:
                if module.io_type not in channels.keys():
                    channels[module.io_type] = module.channels
                else:
                    channels[module.io_type] += module.channels
        return channels
    
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