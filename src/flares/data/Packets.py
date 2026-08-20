from numpy import ndarray
from dataclasses import dataclass

@dataclass(slots=True)
class AnalogCardPacket:
    task_id: int
    packet_index: int
    data: ndarray

@dataclass(slots=True)
class RawPacket:
    packet_index: int
    data: ndarray

@dataclass(slots=True)
class DataPacket:
    packet_index: int
    data: ndarray
    def decimate(self):
        self.data = self.data[:,::10]
        return self