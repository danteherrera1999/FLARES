import dearpygui.dearpygui as dpg
# Give combo boxes categories (user configurable) as well as their names
# Let user pick between a few different timebase buffers
# Let the user select a region from the dynamic plot to static plot it

class MultiPlot:
    def __init__(self, SYSTEM_CONFIG, parent=None):
        self.parent = parent
        self.system_config = SYSTEM_CONFIG
        self.data_buffers = self.system_config["plot buffer"].buffers
        self.channel_map = self.system_config["channel map"]
        self.tag = self.generate_elements()
        self.rate = 1000

    def generate_elements(self):

        with dpg.theme() as self.disabled_theme:
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])

        with dpg.group(horizontal=True, parent=self.parent) as plot_group:
            with dpg.item_handler_registry(tag=f"{plot_group}_combo_right_click_handler"):
                dpg.add_item_clicked_handler(
                    button=dpg.mvMouseButton_Right,
                    callback=self.handle_combo_right_click,
                )

            with dpg.group(tag=f"{plot_group}_combo_group"):
                for i in range(4):
                    with dpg.group(tag=f"{plot_group}_combo_container_{i+1}"):
                        channels = self.system_config["channels"]
                        new_tag = f"{plot_group}_combo_{i+1}"
                        dpg.add_combo(channels, default_value=channels[i % len(channels)],tag=new_tag)
                        dpg.bind_item_handler_registry(new_tag, f"{plot_group}_combo_right_click_handler")
                        with dpg.group(horizontal=True, tag=f"{plot_group}_combo_data_group_{i+1}"):
                            dpg.add_text("mV", tag=f"{plot_group}_chan_{i+1}_unit")
                            dpg.add_text("-100", tag=f"{plot_group}_chan_{i+1}_min")
                            dpg.add_text("100", tag=f"{plot_group}_chan_{i+1}_max")
                dpg.add_combo(
                    [1, 10, 100, 1_000, 10_000],
                    default_value=1_000,
                    callback=self.sample_rate_callback,
                    tag=f"{plot_group}_sr_combo",
                )

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


    def update(self):
        t_arr,data_mat = self.data_buffers[self.rate].get_ordered_data()
        if t_arr.size>0:
            dpg.set_axis_limits(f"{self.tag}_xaxis", t_arr[0], t_arr[-1])
            for i in range(4):
                selected_chan = dpg.get_value(f"{self.tag}_combo_{i+1}")
                chan_idx = self.channel_map[selected_chan]
                dpg.set_value(f"{self.tag}_ls_{i+1}", [t_arr,data_mat[chan_idx]])