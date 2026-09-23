import dearpygui.dearpygui as dpg
import numpy as np 
class ConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_configure"
        self.system_config = SYSTEM_CONFIG
        self.config_store = SYSTEM_CONFIG["config store"]
        self.modules={}
        self.generate_channel_elements()

    def generate_channel_elements(self):
        with dpg.tab(label="Configuration", tag=self.tag):
            dpg.add_button(label="Save",tag="config_save_button",callback=self.handle_save)
            with dpg.tab_bar(label="Config Tab Bar",tag="c_tab_bar"):
                for module in self.system_config["hardware config"].modules:
                    channelElements = []
                    module_name = module.name
                    n = sum(np.array([module.name in name for name in self.modules.keys()]))
                    if n !=0:
                        module_name = f"{module.name}_{n+1}"
                    with dpg.tab(label=module_name):
                        with dpg.table():
                            dpg.add_table_column(label="Type")
                            dpg.add_table_column(label="Channel")
                            dpg.add_table_column(label="Group")
                            dpg.add_table_column(label="Alias")
                            for channel in module.channels:
                                channelElements.append(ChannelConfigElement(channel,module))
                    self.modules[module.name] = channelElements

    def handle_save(self):
        self.config_store.update(self.get_packaged_channel_info())

    def handle_resize(self, new_width, new_height):
        pass

    def update(self): pass

    def get_packaged_channel_info(self):
        channel_info = {}
        for key,channelElements in self.modules.items():
            channel_info[key]=[x.get_channel_info() for x in channelElements]

        return channel_info
    
class ChannelConfigElement:

    def __init__(self,NAME,MODULE):
        self.name = NAME
        self.module = MODULE
        self.tag = f"channel_{self.name}_config"
        self.input_elements = {}
        self.generate_channel_element()

    def generate_channel_element(self):
        with dpg.table_row(tag=f"channel_{self.name}_config"):
            dpg.add_text(self.module.io_type)
            dpg.add_text(self.name)
            self.input_elements["group"]=dpg.add_input_text(tag=f"{self.name}_group_input")
            self.input_elements["alias"]=dpg.add_input_text(tag=f"{self.name}_alias_input")

    def get_channel_info(self):
        channel_info = {}
        for key,input in self.input_elements.items():
            channel_info[key]=dpg.get_value(input)
        return channel_info