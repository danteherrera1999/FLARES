import dearpygui.dearpygui as dpg

class HardwareConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_hardware_configure"
        self.system_config = SYSTEM_CONFIG
        self.channelElemens = self.generate_channel_elements()
        dpg.hide_item(self.tag)
    def generate_channel_elements(self):
        with dpg.tab(label="Hardware Configuration", tag=self.tag):
            pass
        return None

    def handle_resize(self, new_width, new_height):
        pass

    def update(self): pass

    def save_config(self):
        for channel in self.channelElements:
            print(channel.chan_data)