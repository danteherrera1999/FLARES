import dearpygui.dearpygui as dpg
import numpy as np 
import json
from pathlib import Path

class ConfigureTab:

    def __init__(self,SYSTEM_CONFIG):
        self.tag = "window_configure"
        self.system_config = SYSTEM_CONFIG
        self.config_store = SYSTEM_CONFIG["config store"]
        self.config_path = Path("my_config.json")
        self.modules={}
        self.generate_channel_elements()

    def generate_channel_elements(self):
        with dpg.tab(label="Configuration", tag=self.tag):
            dpg.add_button(label="Save",tag="config_save_button",callback=self.handle_save)
            dpg.add_button(label="Save to File", tag="config_file_save_button", callback=self.handle_save_to_file)
            dpg.add_button(label="Load from File", tag="config_file_load_button", callback=self.handle_load_from_file)
            dpg.add_text("", tag="config_file_status")
            with dpg.tab_bar(label="Config Tab Bar",tag="c_tab_bar"):
                for module in self.system_config["hardware config"].modules:
                    channelElements = []
                    module_name = module.name
                    n = sum(np.array([module.name in name for name in [m.name for m in self.modules.keys()]]))
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
                    self.modules[module] = channelElements

    def handle_save(self):
        self.config_store.update(self.get_packaged_channel_info())

    def handle_save_to_file(self):
        config = {
            module.name: channel_info
            for module, channel_info in self.get_packaged_channel_info().items()
        }
        try:
            self.validate_config(config)
            with self.config_path.open("w", encoding="utf-8") as config_file:
                json.dump({"modules": config}, config_file, indent=2)
            dpg.set_value("config_file_status", f"Saved {self.config_path}")
        except (OSError, TypeError, ValueError) as error:
            dpg.set_value("config_file_status", f"Could not save config: {error}")

    def handle_load_from_file(self):
        try:
            with self.config_path.open("r", encoding="utf-8") as config_file:
                saved_config = json.load(config_file)
            if not isinstance(saved_config, dict):
                raise ValueError("unsupported config")
            config = saved_config.get("modules")
            self.validate_config(config)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            dpg.set_value("config_file_status", f"Could not load config: {error}")
            return

        for module, channel_elements in self.modules.items():
            for channel_element, channel_info in zip(channel_elements, config[module.name]):
                for field, value in channel_info.items():
                    dpg.set_value(channel_element.input_elements[field], value)
        runtime_config = {
            module: config[module.name]
            for module in self.modules
        }
        self.config_store.update(runtime_config)
        dpg.set_value("config_file_status", f"Loaded {self.config_path}")

    def validate_config(self, config):
        module_names = {module.name for module in self.modules}
        if not isinstance(config, dict) or set(config) != module_names:
            raise ValueError("hardware mismatch")

        for module, channel_elements in self.modules.items():
            channel_info = config[module.name]
            if not isinstance(channel_info, list) or len(channel_info) != len(channel_elements):
                raise ValueError(f"invalid channel list for module {module.name}")
            for entry in channel_info:
                if (not isinstance(entry, dict)
                        or set(entry) != {"group", "alias"}
                        or any(not isinstance(value, str) for value in entry.values())):
                    raise ValueError(f"invalid channel settings for module {module.name}")

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