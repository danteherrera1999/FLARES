import dearpygui.dearpygui as dpg
import threading
import numpy as np
from flares.gui.widgets.NestedCombo import NestedCombo
# Give combo boxes categories (user configurable) as well as their names
# Let user pick between a few different timebase buffers
# Let the user select a region from the dynamic plot to static plot it

class MultiPlot:
    def __init__(self, SYSTEM_CONFIG, parent=None):
        self.parent = parent
        self.system_config = SYSTEM_CONFIG
        self.config_store = SYSTEM_CONFIG["config store"]
        self.stored_config = None
        self.data_buffers = self.system_config["plot buffer"].buffers
        self.n_ai_mods = -1
        self.channel_map = None
        self.combos = []
        self.generate_elements()
        self.rate = 1000
        self.n_config = -1
        

    def generate_elements(self):

        with dpg.theme() as self.disabled_theme:
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])

        with dpg.group(horizontal=True, parent=self.parent) as self.tag:
            with dpg.item_handler_registry(tag=f"{self.tag}_combo_right_click_handler"):
                dpg.add_item_clicked_handler(
                    button=dpg.mvMouseButton_Right,
                    callback=self.handle_combo_right_click,
                )
            with dpg.group(tag=f"{self.tag}_combo_group",horizontal=False):
                for j in range(4):
                    with dpg.group(tag=f"{self.tag}_combo_container_{j+1}"):
                        self.combos.append(NestedCombo())
                        with dpg.group(horizontal=True, tag=f"{self.tag}_combo_data_group_{j+1}"):
                            dpg.add_text("mV", tag=f"{self.tag}_chan_{j+1}_unit")
                            dpg.add_text("-100", tag=f"{self.tag}_chan_{j+1}_min")
                            dpg.add_text("100", tag=f"{self.tag}_chan_{j+1}_max")

                dpg.add_combo(
                            [1, 10, 100, 1_000, 10_000],
                            default_value=1_000,
                            callback=self.sample_rate_callback,
                            tag=f"{self.tag}_sr_combo",
                        )
            with dpg.plot(tag=f"{self.tag}_plot"):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", tag=f"{self.tag}_xaxis")
                with dpg.plot_axis(dpg.mvYAxis, label="Voltage", tag=f"{self.tag}_yaxis"):
                    for i in range(4):
                        dpg.add_line_series([], [], tag=f"{self.tag}_ls_{i+1}")


    def regenerate_combos(self, new_combo_data):
        if self.stored_config is None:
            return

        for combo in self.combos:
            combo.update_items(new_combo_data)

    def resize(self, width, height):
        plot_tag = f"{self.tag}_plot"
        combo_group_tag = f"{self.tag}_combo_group"
        dpg.set_item_width(plot_tag, 0.8 * width - 20)
        dpg.set_item_height(plot_tag, height - 35)
        dpg.set_item_width(combo_group_tag, 0.2 * width)
        #dpg.set_item_height(combo_group_tag, height)
        for combo in self.combos:
            combo.resize(0.2 * width,height)
        

    def sample_rate_callback(self, sender, app_data, user_data):
        self.rate = int(app_data)

    def handle_combo_right_click(self, sender, app_data, user_data):
        combo_tag = app_data[1]
        ls_tag = combo_tag.replace("combo", "ls")
        if dpg.is_item_shown(ls_tag):
            dpg.hide_item(ls_tag)
            dpg.bind_item_theme(combo_tag, self.disabled_theme)
        else:
            dpg.show_item(ls_tag)
            dpg.bind_item_theme(combo_tag, 0)

    def update_config(self):
        try:
            self.stored_config = self.config_store.get_stored_config()
            self.channel_map = {}
            self.n_ai_mods = 0
            i = 0
            new_combo_data = {}
            for module, module_info in self.stored_config["module info"].items():
                if module.io_type == "Analog Input":
                    self.n_ai_mods += 1
                    for channel in module_info:
                        new_channel_name = channel.alias or channel.name
                        if new_channel_name in self.channel_map.keys():
                            n = sum(np.array([new_channel_name in name for name in list(self.channel_map.keys())]))
                            new_channel_name = f"{new_channel_name}_{n+1}"
                        self.channel_map[new_channel_name] = i

                        channel_group = channel.group or channel.parent
                        if channel_group in new_combo_data.keys():
                            new_combo_data[channel_group].append(new_channel_name)
                        else:
                            new_combo_data[channel_group] = [new_channel_name]
                        i += 1

            self.regenerate_combos(new_combo_data)
            print(f"{self.tag} processed config change to config {self.n_config}")
            return True
        except Exception as e:
            print(e)
            print("Failed to load")

    def update(self):
        n_config = self.config_store.get_n_config()

        if n_config != self.n_config and self.update_config():
            self.n_config = n_config

        if self.n_ai_mods > 0 and self.channel_map:
            t_arr, data_mat = self.data_buffers[self.rate].get_ordered_data()
            if t_arr.size > 0:
                dpg.set_axis_limits(f"{self.tag}_xaxis", t_arr[0], t_arr[-1])
                for i in range(4):
                    selected_chan = self.combos[i].get_value()
                    if selected_chan is None or selected_chan not in self.channel_map:
                        continue
                    chan_idx = self.channel_map[selected_chan]
                    dpg.set_value(f"{self.tag}_ls_{i+1}", [t_arr, data_mat[chan_idx]])