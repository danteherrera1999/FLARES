from numpy import ndarray

@dataclass(slots=True)
class RawPacket:
    packet_index: int
    data: ndarray