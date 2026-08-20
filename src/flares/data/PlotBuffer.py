import numpy as np
from flares.data.DataBuffer import DataBuffer

#This stores our plot data, it is lossful and cyclic, but it is stored contiguously and very efficient
class PlotBuffer:
    def __init__(self):
        self.buffers = {i:x for i,x in [[10**(5-z),DataBuffer(10000,64,10**(5-z))] for z in range(6)]}
        self.decimation = {100:10,
                           10:100,
                           1:1000}

    def extend_all_buffers(self,packet):
        packet_index= packet.packet_index
        self.buffers[100000].extend_from_packet(packet)
        self.buffers[10000].extend_from_packet(packet.decimate())
        self.buffers[1000].extend_from_packet(packet.decimate())
        for rate,decimation in self.decimation.items():
            if packet_index % decimation == 0:
                self.buffers[rate].extend_from_packet(packet)
            else:
                break