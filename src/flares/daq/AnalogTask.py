
import nidaqmx
import numpy as np
from dataclasses import dataclass
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType, Edge, TaskMode
from flares.data.Packets import RawPacket

class AnalogTask():
    def __init__(self, DEVICE_NAMES, OUTPUT_QUEUE):
        self.task = nidaqmx.Task()
        self.device_names = DEVICE_NAMES
        self.channels = [f"{DEVICE_NAME}/ai{i}" for DEVICE_NAME in DEVICE_NAMES for i in range(16)] # Hardcoded 16 channels for now
        self.daq_sampling_rate = 10_000
        self.buffer_size = 2_000
        self.packet_size = 100
        self.output_queue = OUTPUT_QUEUE
        self.read_buffer = np.empty((len(self.channels),self.packet_size),dtype=np.float64) # This buffer temporarily holds data from nidaqmx's internal buffer before being written to a queue
        self.packet_index = 0
        self.reader = AnalogMultiChannelReader(self.task.in_stream)
        self.configure_task()

    def configure_task(self):

        # Configure ai channels
        for channel in self.channels:
            self.task.ai_channels.add_ai_voltage_chan(channel,max_val=10.0,min_val=-10.0)

        # Configure card timing
        self.task.timing.cfg_samp_clk_timing(
            rate=self.daq_sampling_rate,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=self.buffer_size
        )

        # Configure callback
        self.task.register_every_n_samples_acquired_into_buffer_event(
            sample_interval=self.packet_size,
            callback_method=self.task_callback
        )

    def task_callback(self,task_handle,every_n_samples_event_type,number_of_samples,callback_data):
        self.reader.read_many_sample(self.read_buffer,number_of_samples_per_channel=self.packet_size)
        packet_data = self.read_buffer.copy()
        packet_index = self.packet_index
        self.output_queue.put(RawPacket(packet_index,packet_data))
        self.packet_index += 1
        return 0
    
    def start(self):
        self.task.start()

    def stop(self):
        self.task.stop()
        self.task.close()