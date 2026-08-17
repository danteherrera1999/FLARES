
import nidaqmx
import numpy as np
from dataclasses import dataclass
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType

@dataclass(slots=True)
class AnalogCardPacket:
    packet_index: int
    data: np.ndarray

class AnalogTask():
    def __init__(self, DEVICE_NAME,OUTPUT_QUEUE):
        self.task = nidaqmx.Task()
        self.channels = [f"{DEVICE_NAME}/ai{i}" for i in range(16)] # Hardcoded 16 channels for now
        self.device_name = DEVICE_NAME
        self.daq_sampling_rate = 1000
        self.buffer_size = 2000
        self.packet_size = 100
        self.output_queue = OUTPUT_QUEUE
        self.read_buffer = np.empty((16,self.packet_size),dtype=np.float64) # This buffer temporarily holds data from nidaqmx's internal buffer before being written to a queue
        self.packet_index = 0
        self.reader = AnalogMultiChannelReader(self.task.in_stream)
        self.configure_task()

    def configure_task(self):

        # Configure ai channels
        for channel in self.channels:
            self.task.ai_channels.add_ai_voltage_chan(channel)

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
        self.output_queue.put(AnalogCardPacket(packet_index,packet_data))
        self.packet_index += 1
        return 0
    def start(self):
        self.task.start()
    def stop(self):
        self.task.stop()
        self.task.close()