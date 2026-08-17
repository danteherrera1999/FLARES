import numpy as np

#This stores our plot data, it is lossful and cyclic, but it is stored contiguously and very efficient
class DataBuffer:
    def __init__(self, size, total_channels):
        self.size = size
        self.cursor = 0 #This keeps track of the position in the buffer 
        self.filled = False
        self.t = np.zeros(size, dtype=np.float64)
        self.data = np.zeros((total_channels, size), dtype=np.float64)

    def extend(self, new_times, new_data_matrix):
        n = len(new_times)
        if n == 0:
            return
        
        if self.cursor + n <= self.size: #Don't wrap if new data is within buffer
            idx = slice(self.cursor, self.cursor + n) # idx is the data to be REPLACED
            self.cursor += n
        else: #Wraps around if the new data would exceed the buffer size
            self.filled = True
            rem = self.size - self.cursor # data point remaining after filling buffer
            idx = slice(self.cursor, self.size)
            #This replaces the part within the buffer
            self.t[idx] = new_times[:rem]
            self.data[:, idx] = new_data_matrix[:, :rem]
            #idx is reassigned after wrapping to fill the rest of the data
            n_left = n - rem
            idx = slice(0, n_left)
            self.cursor = n_left
            new_times = new_times[rem:]
            new_data_matrix = new_data_matrix[:, rem:]
            
        self.t[idx] = new_times
        self.data[:, idx] = new_data_matrix

    def get_ordered_data(self):

        if not self.filled:
            return self.t[:self.cursor], self.data[:, :self.cursor]
        #Unwraps data and returns it
        t_ordered = np.concatenate((self.t[self.cursor:], self.t[:self.cursor]))
        data_ordered = np.concatenate((self.data[:, self.cursor:], self.data[:, :self.cursor]), axis=1)
        return t_ordered, data_ordered