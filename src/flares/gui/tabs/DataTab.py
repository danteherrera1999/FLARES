import dearpygui.dearpygui as dpg
from gui.widgets.MultiPlot import MultiPlot

class DataTab:
    def __init__(self, SYSTEM_CONFIG):
        self.tag = "window_data"
        self.system_config = SYSTEM_CONFIG
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
                                plots[f"plot {i+2*j+1}"] = MultiPlot(self.system_config,row)
        return plots

    def handle_resize(self, new_width, new_height):
        new_grid_width = int(new_width * 0.75)
        new_grid_height = int(new_height * 0.75)
        dpg.configure_item("plot_grid", width=new_grid_width, height=new_grid_height, pos=[new_width - new_grid_width, 60])
        for plot in self.plots.values():
            plot.resize(int(new_grid_width / 2), int(new_grid_height / 2))

    def update(self):
        for plot in self.plots.values():
            plot.update()
