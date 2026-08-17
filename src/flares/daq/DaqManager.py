from flares.daq.AnalogTask import AnalogTask
from flares.data.Packets import RawPacket
import numpy as np
import queue
import threading

class DaqManager(threading.Thread):
    N_ANALOG_TASKS = 4

    def __init__(self,RAW_DATA_QUEUE,daemon=True):
        super().__init__(daemon=daemon)
        self.raw_data_queue = RAW_DATA_QUEUE
        self.tasks = []
        self.card_packet_queue = queue.Queue()
        self.pending_packets = {}
        self.configure()
        self.stop_event = threading.Event()

    def configure(self):
        for i in range(self.N_ANALOG_TASKS):
            self.tasks.append(AnalogTask(i,f"PXI1Slot{i+2}",self.card_packet_queue))

    def run(self):

        self.start_all_tasks()

        try:
            while not self.stop_event.is_set():
                try:
                    packet = self.card_packet_queue.get(timeout=.1)
                    
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
            task.close()

    def handle_packet(self,packet):

        packet_index = packet.packet_index
        if packet_index not in self.pending_packets:
            self.pending_packets[packet_index] = {}
        packet_frame = self.pending_packets[packet_index]
        packet_frame[packet.task_id] = packet

        if len(packet_frame) == self.N_ANALOG_TASKS:
            self.build_combined_packet(packet_index,packet_frame)
            del self.pending_packets[packet_index]

    def build_combined_packet(self,packet_index,packet_frame):

        packet_size = packet_frame[0].data.shape[1]

        combined_packet_data = np.empty((64,packet_size),dtype=np.float64)

        # Hardcoded for now as it is more efficient than calcultating placement dynamically since this is being called 100 times per second

        combined_packet_data[0:16] = packet_frame[0].data
        combined_packet_data[16:32] = packet_frame[1].data
        combined_packet_data[32:48] = packet_frame[2].data
        combined_packet_data[48:64] = packet_frame[3].data

        self.raw_data_queue.put(RawPacket(packet_index,combined_packet_data))