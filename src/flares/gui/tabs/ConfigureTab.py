import dearpygui.dearpygui as dpg

class ConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_configure"
        self.system_config = SYSTEM_CONFIG
        self.channelElemens = self.generate_channel_elements()

    def generate_channel_elements(self):
        with dpg.tab(label="Configure", tag=self.tag):
            pass
        return None

    def handle_resize(self, new_width, new_height):
        pass

    def update(self): pass

    def save_config(self):
        for channel in self.channelElements:
            print(channel.chan_data)