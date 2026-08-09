import numpy as np
import dearpygui.dearpygui as dpg
import time
import queue
from collections import deque
import multiprocessing
import nidaqmx
from nidaqmx.constants import AcquisitionType
import sys

FR = 60
T = 1 / FR
ACTIVE_PIPES = []
TABS = {}
PLOT_DOWNSAMPLE = 5
BUFFER_SIZE = int(10000/PLOT_DOWNSAMPLE)

DAQ_SAMPLING_RATE = 1000
CALLBACK_INTERVAL = 50
CHANNEL_DTYPES = {
    "Hardware Channel": None,
    "Name": "Input",
    "Measurand":["Voltage","Pressure","Temperature","Strain"],
    "Units":"Input",
}
print(CHANNEL_DTYPES)
channels = 16
DEVICE_NAME = "PXI1Slot2"

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

buffer = DataBuffer(BUFFER_SIZE, channels)
CHANNELS = [f"{DEVICE_NAME}/ai{i}" for i in range(channels)]
CHANNEL_MAP = {ch: i for i, ch in enumerate(CHANNELS)}

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvCombo):
        dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 50])
        dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])

daq_time = 0 # This is for manually tracking time (daqmx does not return timestamps)
task = None # Glob var so I can close the task after the program is shut down

def daq_callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data): # This function takes data and ships it to the different threads and processes
    global daq_time, ACTIVE_PIPES
    try:
        new_data = np.array(task.read(number_of_samples_per_channel=number_of_samples))[:,::PLOT_DOWNSAMPLE]
        new_data_np = np.array(new_data, dtype=np.float64)
        num_samples = new_data_np.shape[1]
        
        time_step = 1.0 / DAQ_SAMPLING_RATE * PLOT_DOWNSAMPLE
        new_times = (daq_time + time_step) + np.arange(num_samples) / DAQ_SAMPLING_RATE
        daq_time = new_times[-1]
        
        buffer.extend(new_times, new_data_np)

        if ACTIVE_PIPES:
            packet = {"t": new_times, "data": new_data_np}
            for pipe in list(ACTIVE_PIPES):
                try:
                    pipe.put_nowait(packet)
                except Exception:
                    ACTIVE_PIPES.remove(pipe)

    except Exception as e:
        print(f"DAQ Error: {e}")
        return -1
    return 0

def data_process():
    global task
    task = nidaqmx.Task()
    for channel in CHANNELS:
        task.ai_channels.add_ai_voltage_chan(channel)
    task.timing.cfg_samp_clk_timing(
        rate=DAQ_SAMPLING_RATE,
        sample_mode=AcquisitionType.CONTINUOUS,
        samps_per_chan=BUFFER_SIZE
    )
    task.register_every_n_samples_acquired_into_buffer_event(
        sample_interval=CALLBACK_INTERVAL,
        callback_method=daq_callback
    )
    task.start()

def detached_plot_process(data_pipe, channel_names):
    def on_detached_close():
        dpg.destroy_context()
        import sys
        sys.exit(0)
    local_buffer = DataBuffer(BUFFER_SIZE, len(channel_names) - 1)
    ch_map = {ch: i for i, ch in enumerate(channel_names[1:])}

    with dpg.window(tag="detached_plot_window") as new_window:
        container = plot_container(new_window)
        
    def process_resize_handler(sender, app_data):
        _, _, w, h = app_data
        container.resize(w, h)
    dpg.set_exit_callback(on_detached_close)
    dpg.set_viewport_resize_callback(process_resize_handler)
    dpg.show_viewport()
    dpg.set_primary_window("detached_plot_window", True)

    t0 = time.perf_counter()

    while dpg.is_dearpygui_running():
        new_data_received = False
        while not data_pipe.empty():
            try:
                pkt = data_pipe.get_nowait()
                local_buffer.extend(pkt["t"], pkt["data"])
                new_data_received = True
            except queue.Empty:
                break
        
        if time.perf_counter() - t0 >= T and new_data_received:
            t0 = time.perf_counter()
            t_arr, data_mat = local_buffer.get_ordered_data()
            if len(t_arr) > 0:
                container.update(t_arr, data_mat, ch_map)

        dpg.render_dearpygui_frame()
    

def open_detached_plot():
    new_queue = multiprocessing.Queue()
    t_arr, data_mat = buffer.get_ordered_data()
    if len(t_arr) > 0:
        new_queue.put_nowait({"t": t_arr, "data": data_mat})
        
    ACTIVE_PIPES.append(new_queue)
    new_process = multiprocessing.Process(
        target=detached_plot_process,
        args=(new_queue, ["t"] + CHANNELS),
        daemon=True
    )
    new_process.start()

def handle_combo_right_click(sender, app_data):
    combo_tag = app_data[1]
    ls_tag = combo_tag.replace("combo", "ls")
    if dpg.is_item_shown(ls_tag):
        dpg.hide_item(ls_tag)
        dpg.bind_item_theme(combo_tag, disabled_theme)
    else:
        dpg.show_item(ls_tag)
        dpg.bind_item_theme(combo_tag, 0)

class plot_container:
    def __init__(self, parent=None):
        self.parent = parent
        self.tag = self.generate_elements()

    def generate_elements(self):
        with dpg.group(horizontal=True, parent=self.parent) as plot_group:
            with dpg.group(tag=f"{plot_group}_combo_group"):
                for i in range(4):
                    with dpg.group(tag=f"{plot_group}_combo_container_{i+1}"):
                        new_tag = f"{plot_group}_combo_{i+1}"
                        dpg.add_combo(CHANNELS, default_value=CHANNELS[i % len(CHANNELS)], tag=new_tag)
                        dpg.bind_item_handler_registry(new_tag, "combo_right_click_logic")
                        with dpg.group(horizontal=True, tag=f"{plot_group}_combo_data_group_{i+1}"):
                            dpg.add_text("mV", tag=f"{plot_group}_chan_{i+1}_unit")
                            dpg.add_text("-100", tag=f"{plot_group}_chan_{i+1}_min")
                            dpg.add_text("100", tag=f"{plot_group}_chan_{i+1}_max")

            with dpg.plot(tag=f"{plot_group}_plot"):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", tag=f"{plot_group}_xaxis")
                with dpg.plot_axis(dpg.mvYAxis, label="Voltage", tag=f"{plot_group}_yaxis"):
                    for i in range(4):
                        dpg.add_line_series([], [], tag=f"{plot_group}_ls_{i+1}")
        return plot_group

    def resize(self, width, height):
        plot_tag = f"{self.tag}_plot"
        combo_group_tag = f"{self.tag}_combo_group"
        dpg.set_item_width(plot_tag, 0.8 * width - 20)
        dpg.set_item_height(plot_tag, height - 35)
        dpg.set_item_width(combo_group_tag, 0.2 * width)
        dpg.set_item_height(combo_group_tag, height)

    def update(self, t_arr, data_mat, ch_map):
        dpg.set_axis_limits(f"{self.tag}_xaxis", t_arr[0], t_arr[-1])
        for i in range(4):
            selected_chan = dpg.get_value(f"{self.tag}_combo_{i+1}")
            chan_idx = ch_map[selected_chan]
            dpg.set_value(f"{self.tag}_ls_{i+1}", [t_arr,data_mat[chan_idx]])

class DataTab:
    def __init__(self):
        self.tag = "window_data"
        self.plots = self.generate_plot_grid()

    def generate_plot_grid(self):
        plots = {}
        with dpg.tab(label="Data", tag=self.tag):
            with dpg.child_window(tag="plot_grid", border=False):
                with dpg.table(header_row=False, borders_innerH=False, borders_innerV=False):
                    for i in range(2):
                        dpg.add_table_column()
                    for i in range(2):
                        with dpg.table_row() as row:
                            for j in range(2):
                                plots[f"plot {i+2*j+1}"] = plot_container(row)
        return plots

    def handle_resize(self, new_width, new_height):
        new_grid_width = int(new_width * 0.75)
        new_grid_height = int(new_height * 0.75)
        dpg.configure_item("plot_grid", width=new_grid_width, height=new_grid_height, pos=[new_width - new_grid_width, 60])
        for plot in self.plots.values():
            plot.resize(int(new_grid_width / 2), int(new_grid_height / 2))

    def update(self, t_arr, data_mat):
        for plot in self.plots.values():
            plot.update(t_arr, data_mat, CHANNEL_MAP)


class channelConfig:
    def __init__(self,hardware_channel):
        self.chan_data = dict.fromkeys(CHANNEL_DTYPES.keys())
        self.chan_data["Hardware Channel"] = hardware_channel
        self.widget_tags = []
        self.tag = self.generate_channel_element()

    def generate_channel_element(self):
        with dpg.table_row() as row:
            for input_label,input_type in CHANNEL_DTYPES.items():
                if input_type is not None:
                    if input_type == "Input":
                        dpg.add_input_text(label=input_label,width=-1,callback=self.value_change_callback)
                    elif isinstance(input_type,list):
                        dpg.add_combo(label=input_label,items=input_type,default_value=input_type[0],width=-1,callback=self.value_change_callback)
            return row

    def resize(self,new_width,new_height):
        pass

    def value_change_callback(self):
        pass

class ConfigureTab:

    def __init__(self):
        self.chanTable = None
        self.channelElements = self.generate_channel_elements()

    def generate_channel_elements(self):
        channelElements = []
        with dpg.tab(label="Configure", tag="window_configure"):
            dpg.add_button(label="Save",callback=self.save_config)
            with dpg.table(resizable=True,policy=dpg.mvTable_SizingStretchProp) as table:
                for i in range(len(CHANNEL_DTYPES)-1):
                    dpg.add_table_column(label=list(CHANNEL_DTYPES.keys())[i+1])
                for i in range(len(CHANNELS)):
                    channelElements.append(channelConfig(CHANNELS[i]))
                self.chanTable = table
        return channelElements

    def handle_resize(self, new_width, new_height):
        dpg.set_item_width(self.chanTable,new_width*.8)

    def update(self): pass

    def save_config(self):
        for channel in self.channelElements:
            print(channel.chan_data)

t0 = time.perf_counter()

def update():
    global t0
    now = time.perf_counter()
    if now - t0 >= T:
        t0 = now
        t_arr, data_mat = buffer.get_ordered_data()
        if len(t_arr) > 0:
            if "DATA" in TABS:
                TABS["DATA"].update(t_arr, data_mat)

with dpg.item_handler_registry(tag="combo_right_click_logic"):
    dpg.add_item_clicked_handler(button=1, callback=handle_combo_right_click)

if __name__ == '__main__':
    data_process()
    
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Tools"):
            dpg.add_menu_item(label="New Detached Plot", callback=open_detached_plot)

    with dpg.window(label="Main", tag="window_main", width=400, height=400):
        dpg.add_spacer(height=20)
        with dpg.tab_bar(label="Tab Bar"):
            TABS["DATA"] = DataTab()
            TABS["CONFIGURE"] = ConfigureTab()

    def viewport_resize_handler(sender, app_data):
        _, _, new_width, new_height = app_data
        for tab in TABS.values():
            tab.handle_resize(new_width, new_height)
    
    dpg.show_viewport()
    dpg.set_primary_window("window_main", True)
    dpg.set_viewport_resize_callback(viewport_resize_handler)
    
    while dpg.is_dearpygui_running():
        update()
        dpg.render_dearpygui_frame()
        
    dpg.destroy_context()

    if task:
        task.stop()
        task.close()