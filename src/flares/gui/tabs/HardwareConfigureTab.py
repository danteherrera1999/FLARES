import dearpygui.dearpygui as dpg

class HardwareConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_hardware_configure"
        self.system_config = SYSTEM_CONFIG
        self.tabs = []
        self.channelElements = self.generate_channel_elements()
        dpg.hide_item(self.tag)
        
    def generate_channel_elements(self):
        with dpg.tab(label="Hardware Configuration", tag=self.tag):
            with dpg.tab_bar(label="Hardware Config Tab Bar",tag="hc_tab_bar"):
                for module in self.system_config["hardware config"].modules:
                    with dpg.tab(label=module.ptype):
                        with dpg.table():
                            dpg.add_table_column(label="Channel")
                            for channel in module.channels:
                                with dpg.table_row():
                                    dpg.add_text(channel)
        return None

    def handle_resize(self, new_width, new_height):
        pass

    def update(self): pass

    def save_config(self):
        for channel in self.channelElements:
            print(channel.chan_data)