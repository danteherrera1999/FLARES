import dearpygui.dearpygui as dpg

class ConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_configure"
        self.system_config = SYSTEM_CONFIG
        self.generate_channel_elements()

    def generate_channel_elements(self):
        self.channelElements = []
        with dpg.tab(label="Configuration", tag=self.tag):
            with dpg.tab_bar(label="Config Tab Bar",tag="c_tab_bar"):
                for module in self.system_config["hardware config"].modules:
                    with dpg.tab(label=module.ptype):
                        with dpg.table():
                            dpg.add_table_column(label="Type")
                            dpg.add_table_column(label="Channel")
                            dpg.add_table_column(label="Group")
                            dpg.add_table_column(label="Alias")
                            for channel in module.channels:
                                self.channelElements.append(ChannelConfig(channel,module))

    def handle_resize(self, new_width, new_height):
        pass

    def update(self): pass

    def save_config(self):
        for channel in self.channelElements:
            print(channel.chan_data)

class ChannelConfig:
    def __init__(self,NAME,MODULE):
        self.name = NAME
        self.module = MODULE
        self.tag = f"channel_{self.name}_config"
        self.generate_channel_element()
    def generate_channel_element(self):
        with dpg.table_row(tag=f"channel_{self.name}_config"):
            dpg.add_text(self.module.io_type)
            dpg.add_text(self.name)
            dpg.add_input_text()
            dpg.add_input_text()